from pathlib import Path

from shared_libraries.utils.get_root_path import get_root_path


class PathConstructor:
    __slots__ = (
        "constructor_path"
    )

    constructor_path: Path

    def __init__(self,
                 constructor_path: Path) -> None:
        self.constructor_path = constructor_path

    def __call__(self,
                 enterprise_id: int) -> Path:
        real_path = Path(self.constructor_path.as_posix().format(enterprise_id=enterprise_id))
        if not real_path.exists():
            real_path.mkdir(parents=True, exist_ok=True)
        return real_path


class DataPathConstructor(PathConstructor):
    def __init__(self,
                 data_folder_name: str = "DATA") -> None:
        super().__init__(
            constructor_path=get_root_path(
                marker_folder=data_folder_name
            ) / data_folder_name / "enterprise_data" / "{enterprise_id}"
        )


if __name__ == '__main__':
    dpc = DataPathConstructor()

    print(dpc(enterprise_id=10))
