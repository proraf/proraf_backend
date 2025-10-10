import factory
from factory import fuzzy
from datetime import date
from proraf.models.user import User
from proraf.models.product import Product
from proraf.models.batch import Batch
from proraf.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    nome = factory.Faker("name", locale="pt_BR")
    email = factory.Faker("email")
    senha = "testpass123"
    tipo_pessoa = fuzzy.FuzzyChoice(["F", "J"])
    cpf = "12345678901"
    cnpj = None
    telefone = factory.Faker("phone_number", locale="pt_BR")
    tipo_perfil = "user"


class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    
    name = factory.Faker("word")
    comertial_name = factory.Faker("company", locale="pt_BR")
    description = factory.Faker("text", max_nb_chars=200)
    variedade_cultivar = factory.Faker("word")
    status = True
    code = factory.Sequence(lambda n: f"PROD-{n:05d}")


class BatchFactory(factory.Factory):
    class Meta:
        model = Batch
    
    code = factory.Sequence(lambda n: f"LOTE-{n:05d}")
    dt_plantio = factory.Faker("date_object")
    dt_colheita = factory.LazyAttribute(lambda o: o.dt_plantio)
    status = True
    talhao = factory.Faker("word")
    producao = fuzzy.FuzzyDecimal(100.0, 10000.0, precision=2)
    product_id = 1
    user_id = 1