'''
# This package is for Chinese language instruction. 
Please install the Chinese font file (kaiu.ttf) in Google Colab platform. 
Installation path: '/content/kaiu.ttf'.
'''
def mops_data(id,yr,sn):  
  import requests
  import json  
  url = 'https://mops.twse.com.tw/mops/api/t163sb01'
  headers = {
      "User-Agent": "Mozilla/5.0",
      "Content-Type": "application/json"
  }
  
  ran = []
  for i in range(1,sn+1):
    ran.append(i) 

  txt = "基本每股盈餘（元）" 
  merge_eps=[]    
  for n in range(1,len(ran)+1):
    myload = {
        "companyId": str(id),
        "dataType": "2",
        "season": n,
        "year": str(yr),
        "subsidiaryCompanyId": ""
    }


    html = requests.post(url, json=myload, headers=headers)
    Response = json.loads(html.text)
    # print(Response) #  ['基本每股盈餘（元）', '45.25', '-', '-']

    # 取得基本每股盈餘（元）
    for item in Response['result']['CCSI']['data']:  
        if item[0] == txt:
            eps = item[1]
            break

    merge_eps.append(eps)
    # print(merge_eps)
    # print(f"第{n}季合併基本每股盈餘（元）: {eps}") # f-string 允許在字串內嵌入變數或表達式

  eps=[]
  for n in range(len(ran)):
    if n == 0:
      EPS = round(float(merge_eps[n]),2)
      eps.append(EPS)
      # print('第',n+1,'季',txt,':',EPS)
    else:
      EPS = round(float(merge_eps[n])-float(merge_eps[n-1]),2)
      eps.append(EPS)
      # print('第',n+1,'季',txt,':',EPS)

  x=ran    # x軸間距
  y=eps    # y軸間距
  import matplotlib.pyplot as plt #pip install matplotlib
  from matplotlib.font_manager import FontProperties
  myFont = FontProperties(fname=r'/content/kaiu.ttf')
  plt.title(label=''+myload.get('companyId')+'公司'+myload.get('year')+'年'+txt+'之趨勢折線圖', 
            loc='center',fontproperties=myFont)
  plt.bar(x,y); plt.plot(x,y)
  plt.ylabel(txt,labelpad=30, fontproperties=myFont) # 設定 y 座標軸標題和間距
  plt.table(cellText=[y],cellLoc='center',rowLabels=['Basic earnings per share'],rowLoc='center', 
            colLabels=x,colLoc='center',loc='bottom',bbox=[0,-0.3,1,0.15]) # bbox=[x,y,w,h]
  plt.savefig('myplot.png')
  plt.show()