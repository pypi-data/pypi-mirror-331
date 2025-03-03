# import matplotlib.pyplot as plt
# import numpy as np
# x=np.linspace(-1,1,400)
# y=x**2
# plt.Figure(figsize=(8,6))
# plt.plot(x,y,linewidth=1,color='green')
# plt.xlim([-1,1])
# plt.ylim([0,3])
# plt.xticks(np.arange(-1,1.5,0.5))
# plt.yticks(np.arange(0,3.5,0.5))
# plt.xlabel(" this is x")
# plt.ylabel(" this is y")
# plt.grid(True)
# plt.show()
#
# # pip install -1 https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/ pandas
# import pandas as pd
# df=pd.read_csv('source.csv')
# df['项目'].replace("",None)
# clean_gender_df=df.loc[df['项目'].isin(['乒乓球','羽毛球'])]
# clean_data=df.loc[df['年龄']>=55]
# df1=clean_data.loc[df['项目']=='乒乓球']
# df2=clean_data.loc[df['项目']=='羽毛球']
# df1.to_csv('out1.csv',index=False,encoding='utf-8')
# df2.to_csv('out2.csv',index=False,encoding='utf-8')
#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# data=pd.read_excel('book_sale.xls',nrows=10)
# plt.rcParams['font.sans-serif']=['SimHei']
# plt.plot(data['月份'],data['数据挖掘\n(单位：万册）'],label='数据挖掘')
# plt.plot(data['月份'],data['计算机组成原理\n(单位：万册）'],label='计算机组成原理')
# plt.plot(data['月份'],data['数据库\n(单位：万册）'],label='数据库')
# plt.legend()
# plt.ylabel('销量（万册）')
# plt.show()
#
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
#     <script src="lib/echarts.min.js"></script>
# </head>
# <body>
#     <div style="width: 600px;height: 400px;">
#     <script>
#         var mcharts=echarts.init(document.querySelector("div"))
#         /** @type EChartsOption */
#         var option={
#             series: [
#                 {
#                     type: 'pie',
#                     data: [
#                         { value: 2, name: '优秀' },
#                         { value: 14, name: '良好' },
#                         { value: 4, name: '一般' },
#                         { value: 4, name: '及格' },
#                         { value: 1, name: '不及格' },
#                     ],
#                 },
#             ],
#         }
#         mcharts.setOption(option)
#     </script>
# </body>
# </html>