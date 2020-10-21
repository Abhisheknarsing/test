from flask import *
import logging
from logging import Formatter, FileHandler
import os
import csv, json
from bigbuy import *
import requests


app = Flask(__name__)

app.config.from_object('config')
app.password = "123"
app.url = "localhost"

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        if request.values.get('password') == app.password:
            session['login'] = True
            return redirect("/seller", code=302)
        else:
            return render_template('pages/placeholder.login.html',result="Wrong Password")
    return render_template('pages/placeholder.login.html')


@app.route('/seller')
def sellers():
    if not session.get('login'):
       return redirect("/", code=302)
    return render_template('pages/placeholder.seller.html')


@app.route('/openSeller')
def openseller():
    if not session.get('login'):
       return redirect("/", code=302)
    select = request.args.get('select')
    filename = request.args.get('filename')
    pro = getjsonbyId(select)
    
    return render_template('pages/placeholder.catselector.html',info=[filename,select],maindata=app.catdata, products=pro)


@app.route('/fetchdata')
def fetch():
    data = Bigbuy()
    data.pullAllData()
    return "success data imported successfully"




@app.route('/assignCategeory')
def assign():
    filename = request.args.get('filename')
    fi = open("bigbuyData/files/config/"+str(filename)+".json","r")
    dat = fi.read()
    lister = dat.split(",")
    f = open("bigbuyData/products_got_from_bigbuy.json","r")
    data = json.loads(f.read())
    f.close()
    finaldata = []
    jsondata=[]
    count=0
    c=0
    zero = False
    with open('bigbuyData/files/'+str(filename)+'.csv', 'w+', newline='', encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile)
        for x in lister:
            if count == 0:
                count=2
                if str(x) == str("0"):
                    zero = True
            else:
                for value in data:
                    if str(value['categeory']) == str(x.split(":")[0]):
                        if zero:
                            if str(value['quantity']) == str(0):
                                continue
                        tempjson = {}
                        tempjson['id'] = value['id']
                        tempjson['sku'] = value['sku']
                        tempjson['quantity'] = value['quantity']
                        jsondata.append(json.dumps(tempjson))
                        if c == 0:
                            spamwriter.writerow(["ID","Name *","Reference #*","Price*","Friendly-url*","Ean-13","UPC","Active(0/1)","visibility(both/catalog/search/none)","Condition(new/used/refurbished)","Available for order (0 = No /1 = Yes)","Show Price","Available online only (0 = No/ 1 = Yes)",	"Short Description",	"Description",	"Tags(xâ€”y--z..)","Wholesale Price","Unit price","Special Price","special price start date","Special Price End Date","On sale (0/1)","Meta Title","Meta Description","Image Url(xâ€”y--z..)","Quantity","Out of stock","Minimal Quantity","Product available date","Text when in stock","Text when backorder allowed","Category Id(x--y--z..)","Default Category id","Width","height","depth","weight","Additional shipping cost","feature(Name:Value)"])
                            spamwriter.writerow([0,value['name'],value['sku'],value['price'],value['url'],value['ean13'],value['upc'],value['active'],value['visiblity'],value['condition'],value['avilableForOrder'],1,value['avilableOnlineOnly'],value['shortDes'],value['description'],value['tags'].replace('&',"and"),value['wholesalePrice'],value['retailPrice'],value['specialPrice'],value['specialPriceSD'],value['specialPriceED'],value['OnSale'],value['metatitle'],value['metadec'],value['images'],value['quantity'],value['outOfStock'],value['minimimQuantity'],value['avilableDate'],value['textInStock'],value['textBackOrder'],x.split(":")[1],x.split(":")[1],value['width'],value['height'],value['depth'],value['weight'],value['shipmentfee'],value['feature']])
                            c = 3
                        else:
                            spamwriter.writerow([0,value['name'],value['sku'],value['price'],value['url'],value['ean13'],value['upc'],value['active'],value['visiblity'],value['condition'],value['avilableForOrder'],1,value['avilableOnlineOnly'],value['shortDes'],value['description'],value['tags'].replace('&',"and"),value['wholesalePrice'],value['retailPrice'],value['specialPrice'],value['specialPriceSD'],value['specialPriceED'],value['OnSale'],value['metatitle'],value['metadec'],value['images'],value['quantity'],value['outOfStock'],value['minimimQuantity'],value['avilableDate'],value['textInStock'],value['textBackOrder'],x.split(":")[1],x.split(":")[1],value['width'],value['height'],value['depth'],value['weight'],value['shipmentfee'],value['feature']])
    
    f = open('bigbuyData/files/'+str(filename)+'.json','w+')
    f.write(json.dumps(jsondata))
    f.close()
    return render_template('pages/download.html',info=[str(filename)])



@app.route('/add')
def add():
    session['filename'] = "something.json"
    filename = session.get('file')
    pid= request.args.get('pid')
    pid = getjsonbyProductId(pid)
    return str(pid)
    
@app.route('/addCat')
def addcat():
    filename = request.args.get('filename')
    pid= request.args.get('id')
    catname = request.args.get('categeory')

    fi = open("bigbuyData/files/config/"+str(filename)+".json","r")
    datatemp = fi.read()
    fi.close()

    fi = open("bigbuyData/files/config/"+str(filename)+".json","w+")
    fi.write(datatemp+','+str(pid)+':'+catname)
    fi.close()
    return "Success"


@app.route('/deleteCard')
def delCard():
    filename = request.args.get('filename')
    os.remove(os.path.join("bigbuyData/files/config",filename))
    return "Removed"

@app.route('/dashboard')
def dash():
    if not session.get('login'):
       return redirect("/", code=302)
    filename = request.args.get('seller')
    arr = os.listdir(os.path.join("bigbuyData/files/config"))

    return render_template('pages/placeholder.dashboard.html',info=[filename],arr = arr)
    

@app.route('/track')
def pulldata():
    filename = request.args.get('filename')
    f = open('bigbuyData/files/'+str(filename)+'.json','r',encoding="utf8")
    data = f.read()
    f.close()
    data = json.loads(data)
    data2 = data
    tempjson = {}
    temp={}
    tempjson["product_stock_request"] = {}
    tempjson["product_stock_request"]["products"] = []
    cout=0
    changes = []
    size = int(len(data)/10 + 1 if not len(data)%10 == 0 else 0)
    for x in data:
        if cout > 8:
            cout = 0
            endpoint = "https://api.bigbuy.eu/rest/catalog/productsstockbyreference.json?isoCode=en"
            output = requests.post(endpoint, headers= {"Authorization": "Bearer NGFkMzI5NGIwMDM1ZmM2ODNkYTZmYTQ3Nzk3MjNjNDNlN2QwZGE5NWIyMjg1YWRkNDA0NzVkOTc1OTA0NTM1NA"},json=tempjson )
            if output.status_code ==200:
                output = output.json()
                for j in data2:
                    j = json.loads(j)
                    for y in output:
                        if j["id"] == y["id"]:
                            if str(j["quantity"]) != str(y["stocks"][0]["quantity"]):
                                if int(y["stocks"][0]["quantity"]) ==0:
                                    changes.append([y['sku'],y["stocks"][0]["quantity"],j["quantity"]])
                                if int(j["quantity"]) == 0:
                                    changes.append([y['sku'],y["stocks"][0]["quantity"],j["quantity"]])
                temp={}
                tempjson = {}
                tempjson["product_stock_request"] = {}
                tempjson["product_stock_request"]["products"] = []
            else:
                print(output.text)
        else:
            
            cout=cout+1
            temp={}
            ktemp = json.loads(x)
            temp["sku"] = ktemp["sku"]
            tempjson["product_stock_request"]["products"].append(temp)
    return render_template('pages/tracker.html',data=changes,filename=[filename])

@app.route('/download')
def download():
    filename = request.args.get('filename')
    return send_from_directory(directory="bigbuyData/files", filename=str(filename)+".csv",as_attachment=True)



@app.route('/changeValue')
def change():
    sku = request.args.get('sku')
    q = request.args.get('quantity')
    filename = request.args.get('filename')
    f = open('bigbuyData/files/'+str(filename)+'.json','r',encoding="utf8")
    data = f.read()
    f.close()
    data = json.loads(str(data))
    new_list = []
    obj = {}
    for x in data:
        y= json.loads(x)
        obj['id'] = str(y['id'])
        obj['sku'] = str(y['sku'])
        if str(y['sku']) == str(sku):
            obj['quantity'] = q
        else:
            obj['quantity'] = str(y['quantity'])
        new_list.append(json.dumps(obj))
        obj = {}

    f = open('bigbuyData/files/'+str(filename)+'.json','w',encoding="utf8")
    f.write(json.dumps(new_list))
    f.close()
    print(new_list)

    return "success"



@app.route('/addCard')
def addCard():
    filename = request.args.get('filename')
    
    catID = request.args.get('zero')
    fi = open("bigbuyData/files/config/"+str(filename)+".json","w+")
    fi.write(catID)
    fi.close()
    return render_template('pages/placeholder.firstcat.html',info=[filename],maindata=app.catdata)


@app.route('/signout')
def signout():
    session.pop('login', None)
    return render_template('pages/placeholder.login.html')


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


file = open("bigbuyData/categeories.txt","r")
app.catdata=file.read()
app.catdata=json.loads(app.catdata)
file.close()

file = open("bigbuyData/products_got_from_bigbuy.json","r")
app.products=file.read()
app.products=json.loads(app.products)
file.close()

def getjsonbyId(catid):
    ran_list_to_save = []
    for x in app.products:
        if int(x['defaultcategeory']) == int(catid):
            ran_list_to_save.append(x)
    return ran_list_to_save

def getjsonbyProductId(idn):
    ran_list_to_save = ""
    with open('bigbuyData/products_got_from_bigbuy.json') as f:
        pdata = json.load(f)
    for y in pdata:
        if str(y['id']) == str(idn):
            return y
    return "none"

if __name__ == '__main__':
    app.run()

