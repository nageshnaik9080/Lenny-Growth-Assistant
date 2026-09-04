import re
from dataclasses import dataclass


@dataclass
class Artifact:
    artifact_type: str
    title: str
    content: str


ARTIFACT_RE = re.compile(
    r'<artifact\s+type=["\'](?P<type>markdown|html)["\']\s+title=["\'](?P<title>[^"\']+)["\']\s*>(?P<body>.*?)</artifact>',
    re.IGNORECASE | re.DOTALL,
)


def extract_artifact(text: str) -> Artifact | None:
    match = ARTIFACT_RE.search(text)
    if not match:
        return None
    return Artifact(
        artifact_type=match.group("type").lower(),
        title=match.group("title").strip(),
        content=match.group("body").strip(),
    )


def remove_artifact_tag(text: str) -> str:
    return ARTIFACT_RE.sub("", text).strip()
