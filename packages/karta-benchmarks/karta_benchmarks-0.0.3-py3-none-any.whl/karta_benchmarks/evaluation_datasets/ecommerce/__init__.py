# Run all the factory functions and return the data
from karta_benchmarks.evaluation_datasets.ecommerce.function_factory.factory import factory as tool_factory
from karta_benchmarks.evaluation_datasets.ecommerce.data_factory.factory import factory as data_factory
from karta_benchmarks.evaluation_datasets.ecommerce.sop.get_sops import sops
from karta_benchmarks.evaluation_datasets.ecommerce.knowledge_base.get_knowledge_base import knowledge_base
from karta_benchmarks.evaluation_datasets.ecommerce.task_factory.factory import factory as task_factory

ARTIFACTS = {
        "tool_factory" : tool_factory,
        "data_factory" : data_factory,
        "sops" : sops(),
        "knowledge_base" : knowledge_base(),
        "tasks" : task_factory()
}