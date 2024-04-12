class Person:
    def __init__(self, firstname: str, lastname: str = None) -> None:
        if not firstname:
            raise ValueError("firstname can't be None")

        self.firstname = firstname
        self.lastname = lastname

    def __eq__(self, other: any) -> bool:
        if isinstance(other, Person):
            return other.firstname == self.firstname and other.lastname == self.lastname
        return False

    def __repr__(self) -> str:
        if self.lastname:
            return f"{self.firstname} {self.lastname}"
        return self.firstname
