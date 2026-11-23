# The World in One Page — 23 November 2026

[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![Rank](https://make.fun/badge/news-image-20261123/Arifpratama19/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![Reward](https://make.fun/badge/news-image-20261123/Arifpratama19/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

A program that sums up the world's news of Monday 23 November 2026 in a single image. Entry for the [news-image-20261123](https://make.fun/bounty/news-image-20261123) bounty on make.fun.

## What it does

`main.py` draws a newspaper front page — masthead, lead story, markets strip, and six more stories — and writes it to `/output/entry.png` as a 1024×1024 PNG. Everything on the page is drawn by the program itself: a hand-built 5×7 bitmap font, rectangles, circles and lines, and a hand-rolled PNG encoder. No images are loaded, no fonts are read from disk, and nothing is fetched from the network, so the output is identical on every run.

## The day it sums up

Monday 23 November 2026, as first reported that day:

- **Lead — United States:** Democrats clinched at least 258 seats in the US House of Representatives, the Associated Press reported — the largest House majority for either party since 1992.
- **Markets:** the AI rout rolled on — the S&P 500 fell 3.7% and the Nasdaq 5.3% on Friday, South Korea's KOSPI dropped 5% on Monday, Asian regulators stepped in, and Dow futures rebounded about 700 points.
- **Iran / Gulf:** President Trump warned Iranian ships running the blockade will be sunk and said he is inclined to resume strikes if no deal is reached by the New Year.
- **Ukraine:** a Ukrainian naval drone severely damaged the Russian corvette Merkury off the Libyan coast, and the cargo ship MV Angara was also hit.
- **Indonesia:** rescuers searched the ruins of a candy factory in Banten after the weekend blaze — 24 confirmed dead, about 30 still missing.
- **Sport:** FIFA was set to confirm the United Kingdom as host of the 2035 Women's World Cup, the first World Cup in the UK since 1966.
- **Tech:** the US sought answers from Nvidia over chip sales to China, and Anthropic shares slid after the company's record IPO.
- **Mexico:** cartel leader Fausto Isidro "Chapo Isidro" Meza-Flores was captured in Sinaloa.

## How to run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024×1024, well under 1 MiB). Python 3 standard library only — no third-party packages, no network access at runtime. Run it twice and the two files are byte-identical.
