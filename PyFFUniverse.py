import PySimpleGUI as sg
import requests
import json
import time

XIVAPIBaseURL = "https://xivapi.com/item/"
DCURL = "https://xivapi.com/servers/dc"

UbaseUrl = "https://universalis.app/api/v2/"
dataCentersU = "data-centers"
worldsU = "worlds"
marketableU = "marketable"

marketableItems = []
itemDictionary = []
printableItems = []
allItemsResponse = {}
itemDB = json.loads('[]')

#print=sg.Print
def open_about(layout):
    window = sg.Window("PyFFUniverse", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()

def switchLanguage(window,Lang):
    global marketableItems
    global itemDictionary
    global printableItems
    global allItemsResponse
    if Lang == "English":
        window["lblLang"].update("Language")
        window["lblDC"].update("Data Center")
        window["lblWorld"].update("World")
        window["lblItemList"].update("List of Items")
        window["btnSearch"].update("Search")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["en"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        window["-ITEMLIST-"].update(values=printableItems)
    elif Lang == "Deutsch":
        window["lblLang"].update("Sprache")
        window["lblDC"].update("Rechenzentrum")
        window["lblWorld"].update("Welt")
        window["lblItemList"].update("Artikelliste")
        window["btnSearch"].update("Suche")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["de"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        window["-ITEMLIST-"].update(values=printableItems)
    elif Lang == "日本語":
        window["lblLang"].update("言語")
        window["lblDC"].update("データセンター")
        window["lblWorld"].update("世界")
        window["lblItemList"].update("詳細")
        window["btnSearch"].update("検索")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["ja"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        window["-ITEMLIST-"].update(values=printableItems)
    elif Lang == "Français":
        window["lblLang"].update("Langue")
        window["lblDC"].update("Centre de données")
        window["lblWorld"].update("Monde")
        window["lblItemList"].update("Liste des articles")
        window["btnSearch"].update("Rechercher")
        itemDictionary = [
            [str(Item), allItemsResponse[str(Item)]["fr"]]
            for Item in marketableItems
        ]
        printableItems = [
            pItem[1]
            for pItem in itemDictionary
        ]
        window["-ITEMLIST-"].update(values=printableItems)

def gatherMarketInfo(dataCenter):
    global marketableItems
    global itemDictionary
    global printableItems
    global allItemsResponse
    global itemDB
    sg.Print("Loading market data. . .")
    try:
        with open("PyFFUniverse.idb", "r") as dbFile:
            itemDB = json.load(dbFile)
    except:
        sg.Print("This is the first time you have run PyFFUniverse. This operation may take some time.")
        #try:
        with open("PyFFUniverse.idb", "w") as idb:
            counter = 0
            for mItem in marketableItems:
                sg.Print(mItem)
                #load data from Universalis
                url = UbaseUrl+dataCenter+'/'+str(mItem)
                data = json.loads(requests.get(url).text)
                print("Appending data...")
                itemDB.append(data)
                print("done. Sleeping for 50 ms")
                time.sleep(0.05)
                counter += 1
                print(counter)
                if counter == 10:
                    break
            json.dump(itemDB, idb)
    sg.Print("Done. You may close this window.")

def main():
    global marketableItems
    global itemDictionary
    global printableItems
    global allItemsResponse
    global itemDB
    sg.theme("default1")
    url = UbaseUrl+marketableU
    response = json.loads(requests.get(url).text)
    marketableItems = [
        item
        for item in response
    ]

    url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/apps/client/src/assets/data/items.json"
    allItemsResponse = json.loads(requests.get(url).text)
    itemDictionary = [
        [str(Item), allItemsResponse[str(Item)]["en"]]
        for Item in marketableItems
    ]
    printableItems = [
        pItem[1]
        for pItem in itemDictionary
    ]

    applicationOptions = [
        [
            sg.T("Language", key="lblLang"),
            sg.Combo(values=["English", "Deutsch", "日本語", "Français"], enable_events=True, key="ddlLanguage")
        ],
        [
            sg.T("Data Center", key="lblDC"),
            sg.Combo(values=["Aether", "Primal", "Crystal"], enable_events=True, key="ddlDC")
        ],
        [
            sg.T("World", key="lblWorld"),
            sg.Combo(values=[], size=(15,1), enable_events=True, key="ddlWorld")
        ],
    ]

    itemListColumn = [
        [
            sg.Text("List of Items",key="lblItemList"),
            sg.In(size=(25, 1), key="txtSearch"),
            sg.Button("Search", key="btnSearch"),
        ],
        [
            sg.Listbox(
                values = printableItems, enable_events=True, size=(40,20), key="-ITEMLIST-"
            )
        ]
    ]

    itemDetailsColumn = [
        #[sg.Text("Debug Output:"),sg.Output(size=(60,20))],
        [
            sg.Text("Item Name:"),
            sg.Text(size=(20,1), key="-ITEMNAME-")
        ]
    ]

    fullLayout = [
        [sg.Text("PyFFUniverse", justification = "center", size=(60,1))
        , sg.Button("About", key="btnAbout")],
        applicationOptions,
        [
            sg.Column(itemListColumn),
            sg.VSeparator(),
            sg.Column(itemDetailsColumn)
        ]
    ]

    aboutWindowLayout=[
        [sg.Text("About PyFFUniverse")],
        [
            sg.Text("This software is copyright 2022 traugdor. All rights are reserved. No portion of this software may be reproduced or copied without express written permission by the author. All data displayed in this software is subject to change without notice. The author of this software bears no responsiblity for the accuracy of the data contained therein. This software is to be used for educational purposes only. If you have enjoyed the use of this software, and would like to donate, please feel free to send donations to Moonmoon Moonmoon on Aether-Jenova."
                , size=(45,15))
        ]
    ]

    window = sg.Window(title="PyFFUniverse", layout=fullLayout)

    while True:
        event, values = window.read()
        #print(event, values);
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        #if someone searched
        if event == "btnSearch":
            searchString = values["txtSearch"]
            updatedList = [
                filteredItem
                for filteredItem in printableItems
                if searchString.upper() in filteredItem.upper()
            ]
            window["-ITEMLIST-"].update(values=updatedList)
        elif event == "btnAbout":
            open_about(aboutWindowLayout)
        #if someone clicked an item
        elif event == "-ITEMLIST-":
            #print(type(values["-ITEMLIST-"][0]))
            itemId = list(filter(lambda x:x[1]==values["-ITEMLIST-"][0], itemDictionary))[0][0]
            #print(itemId)
            url = "".join([XIVAPIBaseURL, str(itemId)])
            #print(url)
            try:
                itemresponse = json.loads(requests.get(url).text)
                window["-ITEMNAME-"].update(itemresponse["Name"])
            except:
                pass
        elif event == "ddlDC":
            try:
                DCResponse = json.loads(requests.get(DCURL).text)
                servers = DCResponse[str(values["ddlDC"])]
                #print(servers)
                window["ddlWorld"].update(values=servers);
                window.Refresh()
                gatherMarketInfo(str(values["ddlDC"]))

            except:
                pass
        elif event == "ddlLanguage":
            eLang = values["ddlLanguage"]
            #print(itemDictionary)
            switchLanguage(window,eLang)

    window.close()

main()
