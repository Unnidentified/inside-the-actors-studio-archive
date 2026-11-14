# Inside the Actors Studio (1994-2018): archival index

A preservation index for *Inside the Actors Studio*: the 277 episodes of the
Bravo and Ovation run, plus the specials and DVD extras that circulate with
them.

The video lives in a public Google Drive folder. This repository holds the
index of what is in it, the tooling that checks the index, and the checklist
the archive is published against.

Archive: [Google Drive public folder](https://drive.google.com/drive/folders/1_3WhsWhf_AUX4JRDNHlkkrN_6O0XfL1f?usp=drive_link)

Discussions: [r/ForgottenTV](https://www.reddit.com/r/ForgottenTV/comments/1wem0ga/inside_the_actors_studio_1994_an_almost_complete/),
[r/DHExchange](https://www.reddit.com/r/DHExchange/comments/1wem2qq/inside_the_actors_studio_1994_an_almost_complete/),
[r/acting](https://www.reddit.com/r/acting/comments/1wenhsn/inside_the_actors_studio_1994_an_almost_complete/)

## Status

| | |
| --- | --- |
| Canonical series episodes | 277 (seasons 1-23) |
| Preserved | 225 (81.2%) |
| Missing | 52 |
| Specials and extras | 13 |
| Video files | 287 across 238 distinct episodes |
| Total size | 165.4 GB |

Episode numbering, air dates and season placement follow the
[Wikipedia episode list](https://en.wikipedia.org/wiki/List_of_Inside_the_Actors_Studio_episodes).
Other episode guides disagree with each other; where they disagree with
Wikipedia, Wikipedia wins.

`itas audit` produces these numbers. It compares the Wikipedia listing, a
snapshot of the Drive folder and the checklist below, and fails if the three
disagree.

## Repository layout

```text
.
├── README.md              # this file
├── itas/                  # the audit tooling
├── data/
│   ├── episodes.json         # canonical episode list, parsed from the wikitext
│   ├── wikipedia_itas.wikitext
│   ├── drive_snapshot.json   # every file and folder in the Drive archive
│   ├── drive_snapshot.csv
│   └── drive_snapshot_files.txt
├── tests/                 # pytest suite, including checks against real data
├── docs/
│   ├── TOOLS.md              # CLI reference and conventions
│   ├── CONTRIBUTING.md       # reporting an episode, working on the code
│   ├── CHANGELOG.md          # archive additions, newest first
│   ├── AGENTS.md             # working notes for coding agents
│   └── known-issues.md       # understood problems that are not yet fixed
└── available-global.txt   # the master post, with the generated checklist
```

Both data files are committed, so the repository can be audited without
network access or credentials.

## Using the tooling

```bash
pip install -e ".[dev]"

itas audit                        # cross-check Wikipedia, Drive and the checklist
itas verify-names                 # check filenames against the convention
itas render                       # print the checklist; --write updates the post
itas index --folder <drive-url>   # refresh the snapshot (needs GDRIVE_API_KEY)
itas parse-wiki                   # rebuild data/episodes.json from the wikitext
```

`itas audit` exits non-zero when something is inconsistent, so it can run in
CI unchanged. Command reference, filename convention and data model are in
[docs/TOOLS.md](docs/TOOLS.md).

## Recent additions

Full history in [docs/CHANGELOG.md](docs/CHANGELOG.md).

* 09/28/2026: Philip Seymour Hoffman (recovered lost episode), Edward Norton broadcast master
* 09/12/2026: mirror threads restored across Reddit
* 09/06/2026: Anthony Quinn, Queen Latifah
* 08/27/2026: Sydney Pollack, Jack Lemmon, Jennifer Jason Leigh, and 10 more
* 05/23/2026: Bernadette Peters, Dave Chappelle, Bryan Cranston, alternate cuts
* 03/01/2026: Sally Field, Dennis Hopper, Neil Simon, Christopher Walken, Martin Landau, Anjelica Huston
* 01/07/2026: Lee Grant, Tommy Lee Jones, Edward Norton, Brad Pitt
* 12/23/2025: Julia Roberts (lost media), Kristen Wiig
* 12/17/2025: initial release, 195 series episodes and 13 specials

## Availability checklist

**Specials / Season 0**

* S00E02 - 100th Episode Special
* S00E03 - 50 Year Celebration
* S00E04 - Robert De Niro (Deleted Scenes) #1
* S00E05 - Robert De Niro (Deleted Scenes) #2
* S00E06 - Robert De Niro (Deleted Scenes) #3
* S00E07 - Robert De Niro (Deleted Scenes) #4
* S00E08 - 200th Episode (Hosted by Dave Chappelle)
* S00E09 - Robin Williams (Extras Combined)
* S00E33 - Paul Newman (Deleted Scenes) #1
* S00E34 - Paul Newman (Deleted Scenes) #2
* S00E35 - Paul Newman (Deleted Scenes) #3
* S00E36 - Paul Newman (Deleted Scenes) #4
* S00E53 - DVD Introduction

**Season 1**

* S01E01 - Paul Newman
* S01E02 - Alec Baldwin
* S01E03 - Stephen Sondheim
* ~~S01E04 - Sidney Lumet~~
* ~~S01E05 - Shelley Winters~~
* S01E06 - Sally Field
* S01E07 - Dennis Hopper
* ~~S01E08 - Arthur Miller~~
* S01E09 - Arthur Penn
* ~~S01E10 - Estelle Parsons~~
* S01E11 - Neil Simon
* S01E12 - Sydney Pollack
* ~~S01E13 - Mary Stuart Masterson~~
* ~~S01E14 - Olympia Dukakis~~
* ~~S01E15 - William Goldman~~

**Season 2**

* S02E01 - Lee Grant
* S02E02 - Faye Dunaway
* S02E03 - Matthew Broderick
* S02E04 - Glenn Close
* ~~S02E05 - Holly Hunter~~
* ~~S02E06 - Ellen Burstyn~~
* S02E07 - Jessica Lange
* ~~S02E08 - Carol Burnett~~
* S02E09 - Christopher Walken
* ~~S02E10 - Gene Wilder~~
* ~~S02E11 - Stanley Donen~~
* S02E12 - Martin Landau

**Season 3**

* ~~S03E01 - Mark Rydell~~
* ~~S03E02 - Norman Jewison~~
* ~~S03E03 - Nathan Lane~~
* S03E04 - Anjelica Huston
* ~~S03E05 - Christopher Reeve~~
* ~~S03E06 - Matt Dillon~~
* S03E07 - Tommy Lee Jones
* ~~S03E08 - Mike Nichols~~
* S03E09 - Julia Roberts
* ~~S03E10 - Meg Ryan~~
* S03E11 - Anthony Quinn
* ~~S03E12 - Willem Dafoe~~
* ~~S03E13 - Billy Crystal~~

**Season 4**

* S04E01 - Harvey Keitel
* ~~S04E02 - Shirley MacLaine~~
* ~~S04E03 - Eli Wallach~~
* ~~S04E04 - Anne Jackson~~
* ~~S04E05 - Lauren Bacall~~
* ~~S04E06 - Martin Short~~
* S04E07 - Anthony Hopkins
* S04E08 - Danny Glover
* S04E09 - Whoopi Goldberg
* S04E10 - Jack Lemmon
* S04E11 - Gary Sinise
* ~~S04E12 - Kathy Bates~~
* ~~S04E13 - Susan Sarandon~~

**Season 5**

* S05E01 - Meryl Streep
* ~~S05E02 - John Hurt~~
* ~~S05E03 - Laurence Fishburne~~
* ~~S05E04 - Donald Sutherland~~
* S05E05 - Ron Howard
* S05E06 - Sharon Stone
* S05E07 - Sean Penn
* S05E08 - Robert De Niro
* S05E09 - Steven Spielberg
* S05E10 - Tim Robbins
* S05E11 - Jennifer Jason Leigh
* S05E12 - Kim Basinger
* ~~S05E13 - Ellen Barkin~~
* S05E14 - Peter Falk
* S05E15 - Jerry Lewis

**Season 6**

* S06E01 - Billy Joel
* ~~S06E02 - Mary Tyler Moore~~
* S06E03 - Sylvester Stallone
* S06E04 - Tom Hanks
* S06E05 - Michael Caine
* S06E06 - Geena Davis
* S06E07 - James Woods
* S06E08 - Andy Garcia
* S06E09 - Kevin Spacey
* S06E10 - Philip Seymour Hoffman
* S06E11 - Alan Alda
* S06E12 - Harrison Ford
* S06E13 - Sigourney Weaver

**Season 7**

* S07E01 - Bernadette Peters
* S07E02 - Val Kilmer
* S07E03 - James Caan
* S07E04 - Richard Dreyfuss
* S07E05 - Gabriel Byrne
* S07E06 - Spike Lee
* S07E07 - Ed Harris
* S07E08 - Ben Affleck
* ~~S07E09 - Ned Beatty~~
* ~~S07E10 - Mike Myers~~
* ~~S07E11 - Michael Douglas~~
* ~~S07E12 - Gwyneth Paltrow~~
* S07E13 - Helen Hunt
* S07E14 - Francis Ford Coppola
* S07E15 - Robin Williams
* S07E16 - Melanie Griffith
* ~~S07E17 - Antonio Banderas~~
* S07E18 - Burt Reynolds
* ~~S07E19 - Roseanne~~

**Season 8**

* S08E01 - Ben Stiller
* S08E02 - Gene Hackman
* ~~S08E03 - Kevin Kline~~
* S08E04 - Bruce Willis
* S08E05 - Kevin Costner
* S08E06 - Will Smith
* S08E07 - Stockard Channing
* ~~S08E08 - Debra Winger~~
* S08E09 - Sarah Jessica Parker
* S08E10 - Ben Kingsley
* S08E11 - Dennis Quaid
* ~~S08E12 - Ethan Hawke~~
* S08E13 - Richard Gere
* S08E14 - Hugh Grant
* S08E15 - Samuel L. Jackson
* S08E16 - Benicio del Toro
* S08E17 - Vanessa Redgrave
* S08E18 - Billy Bob Thornton
* S08E19 - Johnny Depp

**Season 9**

* S09E01 - Sissy Spacek
* S09E02 - Juliette Binoche
* S09E03 - Jeanne Moreau
* S09E04 - Pierce Brosnan
* S09E05 - Ian McKellen
* S09E06 - Martin Scorsese
* S09E07 - Julianne Moore
* S09E08 - Edward Norton
* S09E09 - Cast of The Simpsons
* S09E10 - Nicolas Cage
* S09E11 - Drew Barrymore
* S09E12 - Renée Zellweger
* S09E13 - John Travolta
* S09E14 - Jeremy Irons
* ~~S09E15 - Joanne Woodward~~
* S09E16 - Martin Sheen
* S09E17 - Jeff Bridges

**Season 10**

* S10E01 - John Goodman
* S10E02 - Clint Eastwood
* S10E03 - Cast of Will & Grace
* S10E04 - Cate Blanchett
* S10E05 - Jude Law
* S10E06 - Naomi Watts
* S10E07 - Russell Crowe
* S10E08 - Tom Cruise
* S10E09 - Charlize Theron
* S10E10 - Diane Lane
* S10E11 - Jay Leno
* S10E12 - Hugh Jackman
* S10E13 - Kate Winslet
* S10E14 - Barbra Streisand
* S10E15 - Bette Midler
* S10E16 - 10th Anniversary Special

**Season 11**

* S11E01 - Jennifer Lopez
* S11E02 - James Gandolfini
* S11E03 - William H. Macy
* S11E04 - George Carlin
* S11E05 - Jennifer Connelly
* S11E06 - Mark Wahlberg
* S11E07 - Natalie Portman
* S11E08 - Jamie Foxx
* S11E09 - Salma Hayek
* S11E10 - Morgan Freeman
* S11E11 - Cameron Diaz
* S11E12 - Kiefer Sutherland
* S11E13 - Robert Redford
* ~~S11E14 - Colin Farrell~~
* ~~S11E15 - Val Kilmer - second visit~~
* ~~S11E16 - Owen Wilson~~
* S11E17 - David Duchovny
* S11E18 - Jane Fonda
* S11E19 - Angelina Jolie
* ~~S11E20 - Cast of Everybody Loves Raymond~~
* S11E21 - Jodie Foster
* S11E22 - Elton John
* ~~S11E23 - Rosie O'Donnell~~
* S11E24 - Michael J. Fox

**Season 12**

* S12E01 - Cast of The Producers
* ~~S12E02 - Barbara Walters~~
* S12E03 - Queen Latifah
* S12E04 - Ralph Fiennes
* S12E05 - Martin Lawrence
* S12E06 - Liza Minnelli
* S12E07 - Dave Chappelle
* S12E08 - Cast of Law & Order
* S12E09 - Tom Hanks - second visit
* S12E10 - Don Cheadle
* S12E11 - Tim Allen
* S12E12 - Dustin Hoffman
* S12E13 - Robert Downey Jr.
* S12E14 - Hugh Laurie
* S12E15 - Teri Hatcher
* S12E16 - Al Pacino

**Season 13**

* S13E01 - Forest Whitaker
* S13E02 - Eddie Murphy
* S13E03 - Matt Damon
* S13E04 - Diana Ross
* S13E05 - Chris Rock
* S13E06 - Mark Ruffalo
* S13E07 - Julia Louis-Dreyfus
* S13E08 - Kyra Sedgwick
* S13E09 - Michelle Pfeiffer
* S13E10 - Charlie Sheen
* S13E11 - Billy Crystal - second visit
* S13E12 - Anthony Hopkins - second visit
* S13E13 - Alec Baldwin - second visit
* S13E14 - Halle Berry
* S13E15 - John Cusack

**Season 14**

* S14E01 - Sarah Jessica Parker - second visit
* S14E02 - Mike Myers - second visit
* S14E03 - Brooke Shields
* S14E04 - Christian Slater

**Season 15**

* S15E01 - Goldie Hawn
* S15E02 - Dave Chappelle
* S15E03 - Daniel Radcliffe
* S15E04 - Josh Brolin
* S15E05 - Laura Linney
* S15E06 - Ricky Gervais
* S15E07 - Conan O'Brien
* S15E08 - Anthony LaPaglia
* S15E09 - Denis Leary
* S15E10 - Danny DeVito
* S15E11 - Judd Apatow
* S15E12 - Mickey Rourke
* S15E13 - Jason Bateman
* S15E14 - Cast of Family Guy
* S15E15 - Amy Poehler

**Season 16**

* S16E01 - Hilary Swank
* S16E02 - Jon Bon Jovi
* S16E03 - Kate Hudson
* S16E04 - James Cameron
* S16E05 - Sean Combs
* S16E06 - Betty White

**Season 17**

* S17E01 - James Franco
* S17E02 - Jim Carrey
* S17E03 - Colin Firth
* S17E04 - Bradley Cooper
* S17E05 - Cast of Modern Family
* S17E06 - Jennifer Aniston

**Season 18**

* S18E01 - George Clooney
* S18E02 - Brad Pitt
* S18E03 - Cast of Glee
* S18E04 - Cast of Mad Men
* S18E05 - Liam Neeson

**Season 19**

* S19E01 - Hugh Jackman - second visit
* S19E02 - Tina Fey
* S19E03 - 250th Special - Bradley Cooper, Robert De Niro, Jennifer Lopez, Christopher Walken and Barbara Walters, Dave Chappelle, and more.
* S19E04 - Jake Gyllenhaal
* S19E05 - Cast of Arrested Development
* S19E06 - Bruce and Laura Dern
* S19E07 - Amy Adams

**Season 20**

* S20E01 - Matthew McConaughey
* S20E02 - Cast of How I Met Your Mother
* S20E03 - Mariska Hargitay
* S20E04 - Sting
* S20E05 - Neil Patrick Harris
* S20E06 - Jim Parsons

**Season 21**

* S21E01 - Sarah Silverman
* S21E02 - Bryan Cranston
* ~~S21E03 - Steve Carell~~
* S21E04 - Jeff Daniels
* S21E05 - Cast of The Walking Dead
* S21E06 - Chris Meloni

**Season 22**

* S22E01 - Jessica Chastain
* ~~S22E02 - Viola Davis~~
* ~~S22E03 - Cuba Gooding Jr.~~
* S22E04 - Cast of Girls
* S22E05 - Scarlett Johansson
* S22E06 - Kristen Wiig
* S22E07 - Ted Danson

**Season 23**

* S23E01 - Henry Winkler
* S23E02 - David Oyelowo
* S23E03 - Willem Dafoe (2)
* S23E04 - Al Pacino (2)
* S23E05 - Alfre Woodard
* S23E06 - Laura Dern (2)
* S23E07 - James Burrows
* S23E08 - Lupita Nyong'o

## Contributing

Missing an episode, or have a better copy? See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
Problems that are documented rather than fixed are in
[docs/known-issues.md](docs/known-issues.md).

## Licence

The tooling is MIT licensed. The episodes are not distributed here and remain
the property of their respective rights holders.
