from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import sys
import threading
from threading import Thread
from time import sleep

app = FastAPI()
thread_list = []


@app.get("/")
async def company_jobs_view(company_url: str, page: int = 0):

    url = company_url.split('?')[0]
    if url is not None and page == 0:
        data = company_jobs_scraper(url, 1)
    elif url is not None and page != 0:
        data = company_jobs_scraper(url, page)
    else:
        data = {
            'error': 'The company url was not provided'
        }
    return data


@app.get('/salaries/')
async def get_salaries(company_url: str):
    url = company_url.split('?')[0]
    url = url + '/salaries'
    print(url)
    if url is not None:
        data = salaries_scrapper(url)
    else:
        data = {
            'error': 'The company url was not provided'
        }
    return data


@app.get('/photos/')
async def get_photos(company_url: str, page: int = 0):
    url = company_url.split('?')[0]
    url = url + '/photos'

    print(url)
    if url is not None and page == 0:
        data = photos_scraper(url)
        context = {
            'data': data
        }
        return context

    if page != 0 and url is not None:
        url = url + '?start=' + str((int(page) - 1) * 16)
        data = photos_scraper(url)
        context = {
            'data': data
        }
        return context

    else:
        data = {
            'error': 'The company url was not provided'
        }
        return data


@app.get('/countries/')
async def get_countries_urls():
    data = get_countries()
    context = {
        'data': data
    }
    return context


@app.get('/companies/')
async def companies_view(country_url: str, search: str = ''):
    url = country_url.split('?')[0]
    if url is None:
        return {'data': 'You have to provide the country url'}
    if url is not None and search == '':
        data = company_scraper(url)
        context = {
            'data': data
        }
        return context
    if search != '' and url is not None:
        url = url + '/companies/search?q=' + search
        data = company_search(url)
        print('dta')
        print(data)
        context = {
            'data': data
        }
        return context


def split_url(url):
    base = url.split('/')
    res = '/'.join(base[:3]), '/'.join(base[3:])
    base_url = res[0]
    return base_url


def company_jobs_scraper(url, page=1):
    print(url)
    url += '/jobs/?clearPrefilter=1'
    if page != 1:
        constant = 150
        new_page = (int(page) - 1) * 150
        url += '&start=' + str(new_page)

    base = url.split('/')
    res = '/'.join(base[:3]), '/'.join(base[3:])
    base_url = res[0]
    print(url)
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('Success')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                jobs_div = soup.find('ul', class_='cmp-JobList-jobList')
                print('here')
                print(jobs_div)
                try:
                    all_jobs = jobs_div.find_all('li')
                    print(len(all_jobs))
                    jobs_dict_list = []
                    detail_url_list = []
                    for job in all_jobs:
                        job_dict = {
                            'title': '',
                            'location': '',
                            'posted': '',
                            'job_id': '',
                            'job_detail': '',
                            'job_detail_url': '',
                        }
                        try:
                            title = job.find(class_='cmp-JobListItem-title').text
                        except:
                            title = 'na'
                        try:
                            location = job.find(class_='cmp-JobListItem-subtitle').text
                        except:
                            location = 'na'
                        try:
                            posted = job.find(class_='cmp-JobListItem-timeTag').text
                        except:
                            posted = 'na'
                        try:
                            job_id = job['data-tn-entityid'].split(',')[1]
                        except:
                            job_id = 'na'
                        try:
                            job_id = job['data-tn-entityid'].split(',')[1]
                            print(job_id)
                            job_detail_url = base_url + '/viewjob?jk=' + job_id
                            detail_url_list.append(job_detail_url)
                            print(job_detail_url)
                        except:
                            job_detail_url = 'na'

                        job_dict['title'] = title
                        job_dict['location'] = location
                        job_dict['posted'] = posted
                        job_dict['job_id'] = job_id
                        job_dict['job_detail_url'] = job_detail_url
                        jobs_dict_list.append(job_dict)
                    print(jobs_dict_list)
                    thread_list.clear()
                    for counter, link in enumerate(detail_url_list):
                        print(link)
                        t = Thread(target=detail_scraper, args=(link, jobs_dict_list[counter]['job_id']))
                        t.start()
                        thread_list.append(t)
                    print(thread_list)
                    for b in thread_list:
                        b.join()
                    thread_list.clear()
                    print(job_detail_list)
                    for i, item in enumerate(jobs_dict_list):
                        for j, det in enumerate(job_detail_list):
                            if item['job_id'] == det['job_id']:
                                item['job_detail'] = det
                    print(jobs_dict_list)
                    return jobs_dict_list


                except:
                    print('Could1 not find any jobs')
                    data = {
                        'error': 'Could not find any jobs'
                    }
                    return data
            except:
                print('Could2 not find the jobs div')
                data = {
                    'error': 'Could not find the jobs div'
                }
                return data

        else:
            print('Invalid status code')
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connecting to the server'
        }


job_detail_list = []


def detail_scraper(url, job_id):
    print(url)
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('success')
            soup = BeautifulSoup(page.text, 'html.parser')
            job_detail_dict = {
                'job_id': '',
                'apply_job_url': '',
                'image_logo_url': '',
                'job_detail_text': ''
            }
            try:
                base = url.split('/')
                res = '/'.join(base[:3]), '/'.join(base[3:])
                base_url = res[0]
                apply_job_url = base_url + '/rc/clk?jk=' + job_id
            except:
                apply_job_url = 'na'

            try:
                job_detail_text = soup.text.replace('\n', '')
            except:
                job_detail_text = 'na'
            try:
                company_card = soup.find(class_='icl-Card-body')
                image_logo_url = company_card.find('img')['src']
            except:
                image_logo_url = 'na'
            job_detail_dict['job_id'] = job_id
            job_detail_dict['apply_job_url'] = apply_job_url

            job_detail_dict['image_logo_url'] = image_logo_url
            job_detail_dict['job_detail_text'] = job_detail_text

            print(job_detail_dict)
            job_detail_list.append(job_detail_dict)
        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code'
            }
            job_detail_list.append(data)
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connecting to the server'
        }
        job_detail_list.append(data)


# company_jobs_scraper('https://www.indeed.co.in/cmp/Accenture/jobs', 1)


def salaries_scrapper(url):
    print(url)

    base = url.split('/')
    res = '/'.join(base[:3]), '/'.join(base[3:])
    base_url = res[0]
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('success')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                salary_categories = soup.find(class_='cmp-BrowseByCategoriesDesktop')
                try:
                    all_salaries_categories = salary_categories.find_all('a')
                    print(len(all_salaries_categories))

                    salary_categories_list = []
                    for counter, cat in enumerate(all_salaries_categories):
                        category_dict = {
                            'category_name': '',
                            'category_url': '',
                            'category_data': '',
                            'counter': ''
                        }
                        try:
                            name = cat.text
                        except:
                            name = 'na'
                        try:
                            category_url = base_url + cat['href']
                        except:
                            category_url = 'na'
                        category_dict['category_name'] = name
                        category_dict['category_url'] = category_url
                        category_dict['counter'] = counter
                        salary_categories_list.append(category_dict)
                    thread_list.clear()
                    print(len(thread_list))
                    for category in salary_categories_list:
                        t = Thread(target=category_scraper, args=(category['category_url'], category['counter']))
                        t.start()
                        thread_list.append(t)

                    print(thread_list)
                    print(len(thread_list))
                    for b in thread_list:
                        b.join()

                    print(salaries_results_list)

                    thread_list.clear()
                    print(len(salaries_results_list))
                    print(len(salary_categories_list))
                    for p, i in enumerate(salary_categories_list):
                        print('here')
                        for c in salaries_results_list:
                            print(i)
                            print(salary_categories_list[p]['counter'])

                            print(c)
                            if salary_categories_list[p]['counter'] == c[0]['counter']:
                                salary_categories_list[p]['category_data'] = c

                    print(salary_categories_list)
                    print(len(salary_categories_list))
                    return salary_categories_list

                except:
                    print('Could not find any salaries categories')
                    data = {
                        'error': 'Could not find any salaries categories'
                    }
                    return data
            except:
                print('Could not find any salaries')
        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code'
            }
            return data
    except:
        print('An error occurred while connecting to server')
        data = {
            'error': 'An error occurred while connecting to server'
        }
        return data


salaries_results_list = []


def category_scraper(url, counter):
    print(url)
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('success')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                categories_div = soup.find(class_='cmp-PaginatedCategories')
                try:
                    all_salaries = categories_div.find_all(class_='cmp-SalarySummary')
                    print(len(all_salaries))
                    salaries_list = []
                    for salary in all_salaries:
                        salary_dict = {
                            'job_title': '',
                            'average_salary': '',
                            'counter': ''
                        }
                        try:
                            job_title = salary.find('a').text
                        except:
                            job_title = 'na'
                        try:
                            average_salary = salary.find(class_='cmp-SalarySummaryAverage-salary').text
                        except:
                            average_salary = 'na'
                        salary_dict['job_title'] = job_title
                        salary_dict['average_salary'] = average_salary
                        salary_dict['counter'] = counter
                        salaries_list.append(salary_dict)

                    salaries_results_list.append(salaries_list)


                except:
                    print('Could not find any salaries')
                    data = {
                        'error': 'Could not find any salaries'
                    }
                    salaries_results_list.append(data)
            except:
                print('Could not find the categories div')
                data = {
                    'error': 'Could not find the categories div'
                }
                salaries_results_list.append(data)
        else:
            print('Invalid status code')
            print(page.status_code)
            data = {
                'error': 'Invalid status code',
                'code': page.status_code
            }
            salaries_results_list.append(data)
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connnecting to the server'
        }
        salaries_results_list.append(data)


def photos_scraper(url):
    print(url)
    base = url.split('/')
    res = '/'.join(base[:3]), '/'.join(base[3:])
    base_url = res[0]
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('success')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                main = soup.find('main')
                try:
                    all_images = main.find_all('img')
                    if len(all_images) != 0:
                        print(len(all_images))
                        try:
                            logo_html = soup.find(class_='cmp-CompactHeaderCompanyLogo')
                            try:
                                logo_image = logo_html.find('img')
                                logo_image_dict = {
                                    'image_url': ''
                                }
                                try:
                                    logo_image_url = logo_image['src']
                                except:
                                    logo_image_url = 'na'
                                logo_image_dict['image_url'] = logo_image_url

                            except:
                                print('Could not find the image logo')
                                logo_image_dict = {
                                    'error': 'Could not find the image logo',
                                    'logo_image_url': 'na'
                                }
                        except:
                            print('Could not find the logo html')
                            logo_image_dict = {
                                'error': 'Could not find the logo html',
                                'logo_image_url': 'na'
                            }
                        image_dict_list = []
                        for image in all_images:
                            image_dict = {
                                'image_url': '',
                                'image_description': '',
                            }
                            try:
                                image_url = base_url + image['src'].replace('sqt', 'l')
                            except:
                                image_url = 'na'
                            try:
                                image_description = image['alt']
                            except:
                                image_description = 'na'
                            image_dict['image_url'] = image_url
                            image_dict['image_description'] = image_description
                            image_dict_list.append(image_dict)
                        image_dict_list.append(logo_image_dict)
                        print(image_dict_list)
                        return image_dict_list
                    else:
                        print('Found 0 images')
                        data = {
                            'error': 'Found 0 images'
                        }
                        return data
                except:
                    print('Could not find any photos')
                    data = {
                        'error': 'Could not find any photos'
                    }
                    return data
            except:
                print('Could not find the main section')
                data = {
                    'error': 'Could not find the main section'
                }
                return data
        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code'
            }
            return data
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connecting to the server'
        }
        return data


def get_countries():
    try:
        country_page = requests.get('https://www.indeed.com/worldwide')
        if country_page.status_code == 200:
            print('success')
            country_soup = BeautifulSoup(country_page.text, 'html.parser')
            try:
                countries_div = country_soup.find(class_='countries')
                try:
                    all_countries_link = countries_div.find_all('a')
                    print(len(all_countries_link))
                    final_country_list = []
                    new_country_list = []
                    for i in range(len(all_countries_link)):
                        if i % 2 == 1:
                            new_country_list.append(all_countries_link[i])
                    print(new_country_list)
                    for link in new_country_list:
                        print(link)
                        country_link_dict = {
                            'name': '',
                            'link': ''
                        }
                        try:
                            name = link.text
                        except:
                            name = 'na'
                        try:
                            link = link['href']
                        except:
                            link = 'na'
                        country_link_dict['name'] = name
                        country_link_dict['link'] = link
                        final_country_list.append(country_link_dict)
                    print(final_country_list)

                    return final_country_list


                except:
                    print('Could not find any countries')
                    data = {
                        'error': 'Could not find any countries'
                    }
                    return data
            except:
                print('Couldnot find the country div')
                data = {
                    'error': 'Could not find the country div'
                }
                return data
        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code'
            }
            return data
    except:
        print('An error occurred when trying to connect to the server')
        data = {
            'error': 'An  error occured while trying to connect to the server'
        }
        return data


def company_scraper(url):
    print(url)
    url = url + '/companies'
    base_url = split_url(url)
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('succcess')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                main = soup.find(class_='cmp-discovery-main')
                try:
                    all_companies = main.find_all(class_='icl-Grid-col')
                    print(len(all_companies))
                    company_dict_list = []
                    for company in all_companies:
                        company_dict = {
                            'name': '',

                            'company_url': '',
                            'company_logo_url': ''
                        }
                        try:
                            name = company.find(class_='cmp-PopularCompaniesWidget-companyName').text
                        except:
                            name = 'na'
                        try:
                            company_url = base_url + \
                                          company.find(class_='cmp-PopularCompaniesWidget-companyName').find('a')[
                                              'href']
                        except:
                            company_url = 'na'
                        try:
                            company_logo_url = company.find('img')['src']
                        except:
                            company_logo_url = 'na'
                        company_dict['name'] = name
                        company_dict['company_url'] = company_url
                        company_dict['company_logo_url'] = company_logo_url
                        company_dict_list.append(company_dict)
                    return company_dict_list
                except:
                    print('Could not find any companies')
                    data = {
                        'error': 'Could not find any companies'
                    }
                    return data
            except:
                print('Could not find the main company div')
                data = {
                    'error': 'Could not find the main company div'
                }
                return data

        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code'
            }
            return data
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connecting to the server'
        }
        return data


def company_search(url):
    print(url)
    base_url = split_url(url)
    try:
        page = requests.get(url)
        if page.status_code == 200:
            print('success')
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                main = soup.find(class_='cmp-discovery-main')
                company_dict_list = []
                try:
                    featured_company = main.find(class_='cmp-company-featured-tile')
                    company_dict = {
                        'name': '',
                        'description': '',
                        'company_url': ''
                    }
                    try:
                        name = featured_company.find(class_='cmp-company-tile-blue-name').text
                    except:
                        name = 'na'
                    try:
                        description = featured_company.find(class_='cmp-company-featured-description').text.repalace()
                    except:
                        description = 'na'
                    try:
                        company_url = base_url + featured_company.find('a')['href']
                    except:
                        company_url = 'na'
                    company_dict['name'] = name
                    company_dict['description'] = description
                    company_dict['company_url'] = company_url
                    company_dict_list.append(company_dict)
                except:
                    print('Could not find the featured company')
                try:
                    container = soup.find('ol')
                    try:
                        all_companies = container.find_all('li')
                        print(len(all_companies))
                        for company in all_companies:
                            company_dict = {
                                'name': '',
                                'description': '',
                                'company_url': ''
                            }
                            try:
                                name = company.find('a').text
                            except:
                                name = 'na'
                            try:
                                description = company.find(class_='company_result_description').text
                            except:
                                description = 'na'
                            try:
                                company_url = base_url + company.find('a')['href']
                            except:
                                company_url = 'na'
                            company_dict['name'] = name
                            company_dict['description'] = description
                            company_dict['company_url'] = company_url
                            company_dict_list.append(company_dict)
                        print(company_dict_list)
                        return company_dict_list


                    except:
                        print('Could not find any companies')
                except:
                    print('Could not find the main container')



            except:
                print('Could not find the main section')
                data = {
                    'data': 'could not find the main section'
                }
                return data
        else:
            print('Invalid status code')
            data = {
                'error': 'Invalid status code',
                'code': page.status_code,
            }
    except:
        print('An error occurred while connecting to the server')
        data = {
            'error': 'An error occurred while connecting to the server'
        }
        return data
