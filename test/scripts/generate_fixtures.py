#!/usr/bin/env python3
import random
import argparse
from lettersmith import doc as Doc

PARA_1 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Donec cursus tristique nisi et aliquet. Curabitur posuere
auctor metus at facilisis. Proin ultrices dictum eros non
pharetra. Etiam ultricies pharetra nisl id aliquet. Sed aliquet
efficitur cursus. Nunc aliquet varius tortor, et sollicitudin
libero fermentum sit amet. Phasellus mattis semper magna, congue
laoreet dolor pharetra ac. Proin vitae ornare lacus.
Suspendisse fermentum facilisis congue."""

PARA_2 = """Pellentesque varius rhoncus lacus, sed scelerisque nisl viverra nec.
Mauris sit amet pretium dui. Integer non sapien orci.
In lorem tortor, posuere fringilla efficitur ut, consectetur eu
velit. Nam ornare sapien eu tellus mollis efficitur. Fusce ut
venenatis quam. Quisque ligula ante, iaculis id sollicitudin at,
molestie ac enim. Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Morbi sollicitudin dictum lectus, sodales
rutrum nulla efficitur ut. Nullam congue viverra arcu, a
porttitor nisl dictum quis."""

PARA_3 = """Aliquam erat volutpat. Nulla luctus interdum dui, nec aliquam
lectus aliquet sed. Duis sed purus dictum, posuere leo non,
sollicitudin diam. Praesent malesuada quis sem id euismod.
Maecenas condimentum dictum augue, vitae interdum nibh
vestibulum at. Maecenas arcu massa, scelerisque vitae auctor non,
tempus nec purus. Quisque placerat risus nec tortor luctus, nec
lobortis nisi tristique. Donec non commodo tortor, non tempus enim.
Proin eget iaculis tellus. Curabitur purus ante, fringilla vitae
suscipit a, condimentum sollicitudin ex. In euismod enim sit amet
purus rutrum molestie."""

PARA_4 = """Morbi feugiat felis tellus, nec commodo dui dictum at. Aenean
tincidunt tortor sed tempus placerat. Sed mattis id tellus non
pulvinar. Pellentesque pulvinar semper ultricies. Pellentesque
auctor, lectus sed commodo volutpat, arcu enim luctus odio, at
sodales justo tortor non est. In libero velit, sodales sed elit
ut, elementum scelerisque velit. Morbi eu lacus bibendum, ultrices
purus in, volutpat nisl. Suspendisse posuere dictum auctor.
Vivamus id rutrum nunc. Sed maximus metus nec erat imperdiet
dignissim. Duis sit amet semper urna. Integer non mi tortor."""


PARAS = (PARA_1, PARA_2, PARA_3, PARA_4)


HEADINGS = (
    "Sed maximus metus nec",
    "Volutpat nisil",
    "Elementum velit",
    "Semper urna integer non mi",
    "Vivamus id rutrum nunc"
)


TEMPLATE = """{para_1}

## {heading_2}

{para_2}

{para_3}

- {bullet_1}
- {bullet_2}
- {bullet_3}

## {heading_2}

{para_4}

{para_5}"""


def gen_text():
    """
    Generate some filler markdown text from template
    """
    return TEMPLATE.format(
        para_1=random.choice(PARAS),
        para_2=random.choice(PARAS),
        para_3=random.choice(PARAS),
        para_4=random.choice(PARAS),
        para_5=random.choice(PARAS),
        heading_1=random.choice(HEADINGS),
        heading_2=random.choice(HEADINGS),
        bullet_1=random.choice(HEADINGS),
        bullet_2=random.choice(HEADINGS),
        bullet_3=random.choice(HEADINGS)
    )

def gen_doc(i):
    id_path = "Test Doc {}.md".format(i)
    return Doc.create(
        id_path=id_path,
        output_path=id_path,
        title="Test Doc {}".format(i),
        content=gen_text()
    )


def gen_docs(n):
    for i in range(0, n):
        yield gen_doc(i)


parser = argparse.ArgumentParser(
    description="Generate markdown fixtures"
)
parser.add_argument(
    'n',
    help="Number of documents to generate",
    type=int
)
parser.add_argument(
    'output_path',
    help="Where to write documents",
    type=str,
    default="."
)


def main():
    args= parser.parse_args()
    docs = gen_docs(args.n)
    for doc in docs:
        Doc.write(doc, output_dir=args.output_path)

if __name__ == '__main__':
    main()
