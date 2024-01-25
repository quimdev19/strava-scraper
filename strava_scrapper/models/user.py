from dataclasses import dataclass

@dataclass
class User:

    id: int
    name: str
    location: str = ""
    description: str = ""
    image_url: str = ""
