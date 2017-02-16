# coding utf-8
from faker import Factory

fake = Factory.create('it_IT')
fake_jp = Factory.create('ja_JP')

TYPES = {
    'int': int,
    'randint': lambda x: randint(0, int(x)),
    'randuuid': lambda x: str(uuid4()),
    'rand_year': lambda x: fake.year(),
    'first_name_female': lambda x: fake.first_name_female(),
    'first_name_male': lambda x: fake.first_name_male(),
    'last_name': lambda x: fake.last_name(),
    'rand_date_time': lambda x: str(fake.date_time()),
    'randate': lambda x: fake.date(),
    'day_of_month': lambda x: fake.day_of_month(),
    'user_name': lambda x: fake.user_name(),
    'randmonth': lambda x: '{}'.format(fake.month()),
    'phone_number': lambda x: str(fake.phone_number()),
    'jap_name': lambda x: fake_jp.first_name_female(),
    'jap_surname': lambda x: fake_jp.last_name_female(),
    'jap_string': lambda x: fake_jp.text(),
    'suffix_male_jp': lambda x: ' '.join(fake_jp.suffix_male() for n in range(10)),
    'city': lambda x: fake.city(),
    'country_code': lambda x: fake.country_code(),
    'address': lambda x: fake.address(),
    'text': lambda x: (fake.text(), '')[randint(0,1)],
    'addrs_typ': lambda x: ['Billing', 'Shipping', 'Residence', 'Working address', 'Second Home', 'Other address', 'Alternative Service Address', 'Domicile'][randint(0,7)],
    'word': lambda x: (fake.word(), '')[randint(0,1)],
    'maybe_name': lambda x: (fake.name(), '')[randint(0,1)],
    'letter': lambda x: (fake.random_letter(), '')[randint(0,1)],
    'brand': lambda x: ['MM','WE','SP','MC','MA','IB','PB','MR','PE','IN','DT'][randint(0,10)],
    'canale': lambda x: ['TRANSITO','PASSAPAROLA','ACCOMPAGNATORE','COMUNICAZIONE_PV','MEDIA','SOCIAL_NETWORK','ALTRO',''][randint(0,6)],
    'tipo_cons': lambda x: ['Marketing Diretto','Profilazione','Comunicazione a terze parti','Comunicazione'][randint(0,3)],
    'email': lambda x: (fake.email(), '')[randint(0,1)],
    'brand_label': lambda x: ['MaxMara','Sportmax','Weekend MaxMara','Max&Co.','Marella','iBlues','PennyBlack','Marina Rinaldi','Persona','Diffusione Tessile',''][randint(0,9)],
    'priority': lambda x: ['High', 'Low', 'Medium'][randint(0,2)],
    'promotyp': lambda x: ['gift', 'promo_valore', 'promo_percentuale'][randint(0,2)],
    'cod_negozio': lambda x: ['0100019', '0100039', '0100035'][randint(0,2)],
}
