from .web import URL

type StringDict = dict[str, str]


class Identifier(URL):
    def __new__(cls, url: URL | str, strict: bool = False):
        if isinstance(url, URL):
            _url = url
        else:
            _url = URL(url)

        return super().__new__(
            cls,
            URL.build(
                scheme="id",
                username=_url.username,
                password=_url.password,
                host=_url.host_root.lower(),
                path=_url.path.rstrip("/"),
                query=_url.query_params("flat"),
            ),
        )

    @property
    def root(self) -> URL:
        """
        Return ID without zz_* parameters
        """

        return URL(self).update(
            query={
                k: v
                for k, v in self.query_params("flat").items()
                if not k.startswith("zz_")
            }
        )

    @property
    def domain(self) -> str:
        return self.host
