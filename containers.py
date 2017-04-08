# coding utf-8
import re
import json
import requests
import os
from collections import OrderedDict
from pprint import pprint

from tools import json_load_byteified, recursive_json_loads, make_iteritems

VARIABLES_REGEX = r'(?<=<\$)([^\$]*)(?=\$>)'
REMOVETYPE_REGEX = r'\|([^\$]*)(?=\$>)'


class SuiteNamespaceAccessor(object):
    _vars = {}
    _var_map = {}

    def __init__(self):
        super(SuiteNamespaceAccessor, self).__init__()

    def _vars_values(self):
        return {var.name: var.value for var in self._vars.values()}

    def _extract_variables(self, obj):
        for k, v in make_iteritems(obj):
            if isinstance(v, basestring):
                try:
                    jobj = json.loads(obj)
                except:
                    for var in re.findall(VARIABLES_REGEX, v):
                        var = ReqVariable(var)
                        if var.name not in self._vars:
                            self._vars[var.name] = var
                        if var.type:
                            self._vars[var.name] = var
                            self._vars[var.name].set_val()
                else:
                    self._extract_variables(jobj)
            else:
                self._extract_variables(v)

    def _insert_variable_value(self, string):
        try:
            string = re.sub(REMOVETYPE_REGEX, '', string)
            req_vars = re.findall(VARIABLES_REGEX, string)
            req_vars = {vname: self._vars[vname].get_val() for vname in req_vars}
            string = string.replace('{','#[#').replace('}','#]#').replace('<$','{').replace('$>','}').format(**req_vars).replace('#[#','{').replace('#]#','}')
        except Exception as ex:
            pass
        return string

    def _find_vars(self, content):
        for k, v in content.iteritems():
            if k in self._vars:
                self._vars[k].value = v
            if isinstance(v, dict):
                self._find_vars(v)
            if isinstance(v, list):
                for item in v:
                    self._find_vars(item)


class ReqVariable(object):

    def __init__(self, name):
        super(ReqVariable, self).__init__()
        info = name.split('|')
        x = tuple(attr for attr in info + [None] * (3-len(info)))
        self.name, self.type, self.value = x
        self.name = info[0]

    def set_val(self, value=None):
        value = value or self.value
        if self.type:
            try:
                self.value = self.var_map[self.type](value)
            except Exception as ex:
                pass
        else:
            self.value = value

    def get_val(self):
        if isinstance(self.value, unicode):
            self.value = self.value.encode('utf-8')
        if isinstance(self.value, basestring):
            self.value = self.value.replace('\n', ' ').replace('\r', '')
        return self.value


class RequestTest(SuiteNamespaceAccessor):

    def __init__(self, request):
        super(RequestTest, self).__init__()
        self.url = request['url']
        self.body = recursive_json_loads(request['rawModeData'])
        self.method = request['method']
        name = request['name'].upper().split()
        self.resource = name[0]
        self.repetitions = name[-1] if 'REPEATE' in name else 1
        self.headers = {}
        for header in request['headers'].split('\n'):
                header = header.split(': ')
                if len(header) > 1:
                    if header[1]:
                        self.headers[header[0]] = header[1]
        self._extract_variables(self.body)

    def _prepare_url(self):
        return self._insert_variable_value(self.url.strip())

    def _prepare_obj(self, obj):
        if isinstance(obj, basestring):
            return self._insert_variable_value(obj)
        elif isinstance(obj, list):
            return [self._prepare_obj(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: self._prepare_obj(v) for k, v in obj.iteritems()}
        else:
            return obj

    def _prepare_body(self):
        self._extract_variables(self.body)
        body = self._prepare_obj(self.body)
        if isinstance(body, basestring):
            return body
        return json.dumps(body)

    def send(self):
        for _ in range(self.repetitions):
            url = self._prepare_url()
            body = self._prepare_body()
            resp = requests.request(self.method, url, data=body, headers=self.headers)
            if resp.status_code in (200, 204):
                yield (resp.status_code, recursive_json_loads(resp.content))
            else:
                yield (resp.status_code, resp.content)


class Collection(SuiteNamespaceAccessor):

    def __init__(self):
        super(Collection, self).__init__()
        self.requests = OrderedDict()

    def add_var_map(self, var_map):
        self._var_map.update(var_map)

    def suite_from_file(self, file_path):
        file_path = os.path.join(os.getcwd(), file_path)
        with open(file_path) as jfile:
            req_collection = json_load_byteified(jfile)
        reqs = req_collection['requests']
        order = req_collection['order']
        reqs.sort(key=lambda request: order.index(request['id']))
        for req in reqs:
            req = RequestTest(req)
            self.requests[(req.resource, req.method)] = req

    def run(self, delete=True):
        for k, req in self.requests.iteritems():
            if not delete and req.method in ('DELETE', 'PATCH', 'GET'):
                continue
            for response in req.send():
                if response[0] == 200:
                    self._find_vars(response[1])
                elif response[0] == 204:
                    response = self.requests[(req.resource, 'POST')].send()
                    if response[0] == 200:
                        self._find_vars(response[1])


c = Collection()
c.suite_from_file('CRM.json')
from uuid import uuid4
c.add_var_map({'int': int, 'randuuid': lambda x: str(uuid4()),})
pprint({k: v.__dict__ for k, v in c._vars.iteritems()})
#c.run(delete=False)
