from karta_benchmarks.namespaces.domains import Domains

class ContextEngine:
    def __init__(self, domain: Domains):
        self.domain = domain
        # Loads all the data for the domain
        if domain == Domains.ECOMMERCE:
            from karta_benchmarks.evaluation_datasets.ecommerce import ARTIFACTS
            self._artifacts = ARTIFACTS
        else:
            raise ValueError(f"Domain {domain} not supported")
        print(f"======== Created Context Engine for {domain.value} ========")

    @property
    def artifacts(self) -> dict:
        return self._artifacts    


