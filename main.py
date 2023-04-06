import re
import requests
from bs4 import BeautifulSoup as bs

url_address = "https://www.imdb.com/"
tv_show = {}


def get_urls_address():
    urls = []
    main_address_url = url_address + "chart/tvmeter/"
    response = requests.get(main_address_url)
    soup = bs(response.content, 'html.parser')
    column = soup.findAll("td", attrs={"class", "titleColumn"})
    for i in range(len(column)):
        urls.append(column[i].find("a").get('href'))
    return urls


def scrapSubPage(url):
    response = requests.get(url_address + url)
    sub_soup = bs(response.content, "html.parser")
    card = sub_soup.find("div", class_="ipc-page-content-container ipc-page-content-container--full sc-b1984961-0 "
                                       "kXDasd")
    # Tytuł
    title = card.find("h1", attrs={'class': 'sc-b73cd867-0'}).text.strip()
    tv_show['title'] = title
    print(title)

    # Twórcy
    creators_span = card.find("span", string=re.compile('Creators+'))
    if creators_span is None:
        tv_show['creators'] = []
    else:
        creators_section = card.find("span", string=re.compile('Creators+')).findNext("div")
        creator_sections = creators_section.find_all("a")
        creators = [x.text for x in creator_sections]
        tv_show['creators'] = creators
        print(creators)

    # Gwiazdy
    stars_span = card.find("a", string=re.compile('Stars+'))
    if stars_span is None:
        tv_show['stars'] = []
    else:
        stars_section = card.find("a", string=re.compile("Stars+")).findNext("div")
        stars_sections = stars_section.find_all("a")
        stars = [s.text for s in stars_sections]
        tv_show['stars'] = stars
        print(stars)

    # Kategorie
    category_section = card.find("div", attrs={'class': 'ipc-chip-list sc-16ede01-4 bMBIRz'})
    if category_section is None:
        category_section = card.find("div", attrs={'class': 'ipc-chip-list sc-16ede01-5 ggbGKe'})
    categories_sections = category_section.find_all("a")
    categories = [c.text for c in categories_sections]
    tv_show['categories'] = categories
    print(categories)

    # Data wydania
    release_date_span = card.find("a", string=re.compile('Release date+'))
    if release_date_span is None:
        tv_show['release_date'] = []
    else:
        release_date_section = card.find("a", string=re.compile('Release date+')).findNext("div")
        release_date_sections = release_date_section.find_all("a")
        release_date = [x.text for x in release_date_sections]

        tv_show['release_date'] = release_date
        print(release_date)

    # Kraj pochodzenia
    country_of_origin_span = card.find("span", string=re.compile('Country of origin+'))
    if country_of_origin_span is None:
        tv_show['country_of_origin'] = []
    else:
        country_section = card.find("span", string=re.compile('Country of origin+')).findNext("div")
        country_sections = country_section.find_all("a")
        country_of_origin = [x.text for x in country_sections]
        tv_show['country_of_origin'] = country_of_origin
        print(country_of_origin)

    # Oficjalna strona
    official_site_span = card.find("span", string=re.compile('Official site+'))
    if official_site_span is None:
        tv_show['official_site'] = []
    else:
        site_section = card.find("span", string=re.compile('Official site+')).findNext("div")
        site_sections = site_section.find_all("a")
        official_site = [x.text for x in site_sections]
        tv_show['official_site'] = official_site
        print(official_site)

    # Język
    language_span = card.find("span", string=re.compile('Language+'))
    if language_span is None:
        tv_show['language'] = []
    else:
        language = card.find("span", string=re.compile('Language+')).findNext("div")
        languages = language.find_all("a")
        languages = [x.text for x in languages]
        tv_show['language'] = languages
        print(languages)

    # Lokacja
    location_span = card.find("a", string=re.compile('Filming locations+'))
    if location_span is None:
        tv_show['location'] = []
    else:
        location = card.find("a", string=re.compile('Filming locations+')).findNext("div")
        locations = location.find_all("a")
        locations = [x.text for x in locations]
        tv_show['location'] = locations
        print(locations)

    # Produkcja
    production_span = card.find("a", string=re.compile('Production companies+'))
    if production_span is None:
        tv_show['production_companies'] = []
    else:
        production = card.find("a", string=re.compile('Production companies+')).findNext("div")
        production_companies = production.find_all("a")
        production_companies = [x.text for x in production_companies]
        tv_show['production_companies'] = production_companies

        print(production_companies)

    return tv_show


def create_show(show):
    show_title = show['title']
    show_creators = show['creators']
    show_stars = show['stars']
    show_categories = show['categories']
    show_release_date = show['release_date']
    show_country_of_origin = show['country_of_origin']
    show_official_site = show['official_site']
    show_language = show['language']
    show_location = show['location']
    show_production_companies = show['production_companies']
    show_title = show_title.replace(" "" ", " ")

    # Show
    script = f"\nMerge (s:Show{{title: '{show_title}', release: '{show_release_date[0]}', country: '{show_country_of_origin}'}})"

    # Twórcy
    for i in range(0, len(show_creators)):
        script += f"\nMerge (cr{i + 1}:Creator{{Name: '{show_creators[i]}'}})"
        script += f"\nMerge (cr{i + 1})-[:is_creating]->(s)"

    # Gwiazdy
    for i in range(0, len(show_stars)):
        script += f"\nMerge (st{i + 1}:Star{{Name: '{show_stars[i]}'}})"
        script += f"\nMerge (st{i + 1})-[:is_playing_in]->(s)"

    # Kategorie
    for i in range(0, len(show_categories)):
        script += f"\nMerge (c{i + 1}:Category{{Name: '{show_categories[i]}'}})"
        script += f"\nMerge (s)-[:is_category]->(c{i + 1})"

    # Miejsce
    for i in range(0, len(show_location)):
        script += f"\nMerge (l{i + 1}:Location{{Name: '{show_location[i]}'}})"
        script += f"\nMerge (s)-[:is_recorded_in]->(l{i + 1})"

    # Język
    for i in range(0, len(show_language)):
        script += f"\nMerge (le{i + 1}:Language{{Name: '{show_language[i]}'}})"
        script += f"\nMerge (s)-[:is_in_language]->(le{i + 1})"

    # Oficjalna strona
    for i in range(0, len(show_official_site)):
        script += f"\nMerge (si{i + 1}:Site{{Name: '{show_official_site[i]}'}})"
        script += f"\nMerge (s)-[:issued_by]->(si{i + 1})"

    # Produkcja
    for i in range(0, len(show_production_companies)):
        script += f"\nMerge (p{i + 1}:Production Companies{{Name: '{show_production_companies[i]}'}})"
        script += f"\nMerge (s)-[:produced_by]->(p{i + 1})"

    script += ";"
    return script


def main():
    script = ""
    for url in get_urls_address():
        script += create_show(scrapSubPage(url))
    print(script)
    with open("Skrypt.txt", "w", encoding="UTF-8") as sc:
        sc.write(script)


main()
