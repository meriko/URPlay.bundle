TITLE  = 'UR Play'
PREFIX = '/video/urplay'

ART  = R('art-default.jpg')
ICON = R('icon-default.png')

BASE_URL = 'http://www.urplay.se'

HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17"

####################################################################################################
def Start():
    # Set the default ObjectContainer attributes
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = ART
    
    DirectoryObject.thumb = ICON

    # Set the default cache time
    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = HTTP_USER_AGENT

####################################################################################################
@handler(PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer()
    
    element = HTML.ElementFromURL(BASE_URL)
    
    for item in element.xpath("//ul//li"):
        link = item.xpath(".//a/@href")[0]
        
        if link == '/':
            continue
        
        title = unicode(item.xpath(".//a/text()")[0]) 
        
        if link == '/A-O':
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            AllPrograms,
                            url = BASE_URL + link,
                            title = title
                        ),
                    title = title
                )
            )
            break # last
        else:
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Videos,
                            url = BASE_URL + link,
                            title = title
                        ),
                    title = title
                )
            )
    
    title = unicode("Sök")
    oc.add(
        InputDirectoryObject(
            key = Callback(Search, title = title),
            title  = title,
            prompt = title,
            thumb = ICON
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/AllPrograms')
def AllPrograms(url, title):
    oc = ObjectContainer(title2 = unicode(title))
    
    element = HTML.ElementFromURL(url)
    
    for item in element.xpath("//*[@id='alphabet']//a"):
        try:
            type = item.xpath(".//span/@class")[0]
        except:
            continue
        
        if type != 'product-type tv':
            continue
            
        title = item.xpath("./text()")[0].strip()
        link  = item.xpath("./@href")[0]
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Videos,
                        url = BASE_URL + link,
                        title = title
                    ),
                title = title
            )
        )
        
    return oc
    
####################################################################################################
@route(PREFIX + '/Videos', page = int)
def Videos(url, title, page = 1):
    oc = ObjectContainer(title2 = unicode(title))
    
    requestURL = url
    if '?' in requestURL:
        requestURL = requestURL + '&page=' + str(page)
    else:
        requestURL = requestURL + '?page=' + str(page)
        
    element = HTML.ElementFromURL(requestURL)
    
    for item in element.xpath(".//section[@class='tv']"):
        try:
            link  = item.xpath(".//a/@href")[0]
            title = unicode(item.xpath(".//h1/text()")[0]).strip()
        except:
            continue

        try:
            show = unicode(item.xpath(".//h2/text()")[0]).strip()
            if show == title:
                show = None
        except:
            show = None

        try:
            summary = unicode(item.xpath(".//p/text()")[0]).strip()
        except:
            summary = None
            
        try:
            thumb = item.xpath(".//img/@src")[0]
        except:
            thumb = ICON
        
        try:
            durationString = item.xpath(".//dd/text()")[0]
            duration       = (int(durationString.split(':')[0]) * 60 + int(durationString.split(':')[1])) * 1000
        except:
            duration = None
        
        try:
            originally_available_at = Datetime.ParseDate(item.xpath(".//time/@datetime")[0].split('T')[0]).date()
        except:
            originally_available_at = None
        
        oc.add(
            EpisodeObject(
                url = BASE_URL + link,
                title = title,
                show = show,
                summary = summary,
                thumb = thumb,
                duration = duration,
                originally_available_at = originally_available_at
            )
        )
        
    for item in element.xpath("//*[@class='pagination']//a/text()"):
        if item == '>':
            oc.add(
                NextPageObject(
                    key =
                        Callback(
                            Videos,
                            url = url,
                            title = title,
                            page = page + 1
                        ),
                    title = 'Fler...'
                )
            )
            break
        
    return oc

####################################################################################################
@route(PREFIX + '/Search')
def Search(query, title):
    oc = ObjectContainer(title2 = unicode(title))

    result = Videos(
        url = BASE_URL + '/Produkter?q=' + String.Quote(query),
        title = unicode('Resultat för : "') + query + '"'
    )
    
    if len(result) > 0:
        return result
    else:
        oc.header  = unicode('Inga program funna')
        oc.message = unicode('Din sökning på : "') + query + '" gav inget resultat'
        return oc
