#filename:Server+SwitchButton.py
#-*-coding:utf-8-*-

import Tkinter
import tkFont
import socket
import thread
import time
import urllib
import urllib2
import traceback
import MySQLdb
import random
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Server():
    title = 'Python自动客服-服务器'
    Ip = '127.0.0.1'#经测只能用外网ip设置serverIp
    Port = 8808#端口必须在1024以上
    global serverSock
    global receiveMsg
    global message
    flag = False

    #初始化类的相关属性，类似于构造方法
    def __init__(self):
        from Tkinter import *
        self.root = Tkinter.Tk()
        self.root.title(self.title)

        #窗口面板,用6个frame面板布局，ip和port设置框架最后因为连接方式的选取问题取消
        self.frame = [Tkinter.Frame(), Tkinter.Frame(), Tkinter.Frame(), Tkinter.Frame(), Tkinter.Frame(), Tkinter.Frame()]

        #frame0
        #切换功能的checkButton
        self.CheckVar1 = IntVar()
        self.CheckVar2 = IntVar()
        self.CheckVar3 = IntVar()
        self.CheckButton1 = Checkbutton(self.frame[0], text = "手动", variable = self.CheckVar1, onvalue = 1, offvalue = 0, height=2, width = 5)
        self.CheckButton2 = Checkbutton(self.frame[0], text = "数据库", variable = self.CheckVar2, onvalue = 1, offvalue = 0, height=2, width = 5)
        self.CheckButton3 = Checkbutton(self.frame[0], text = "图灵", variable = self.CheckVar3, onvalue = 1, offvalue = 0, height=2, width = 5)
        self.CheckButton1.pack(expand=1, side=Tkinter.TOP and Tkinter.LEFT)
        self.CheckButton2.pack(expand=1, side=Tkinter.TOP and Tkinter.LEFT)
        self.CheckButton3.pack(expand=1, side=Tkinter.TOP and Tkinter.RIGHT)
        self.frame[0].pack(fill=Tkinter.BOTH)#expand=1,

        '''
        #frame1
        #ip地址和端口选择，暂时取消
        ft1 = tkFont.Font(family='Fixdsys', size=8)
        self.inputTextIp = Tkinter.Text(self.frame[1], width=20, height=2, font=ft1)
        self.inputTextPort = Tkinter.Text(self.frame[1], width=7, height=2, font=ft1)
        self.ipConfirmButton = Tkinter.Button(self.frame[1], text='确认', width=5, height=2, command=self.setIpPort)
        self.inputTextIp.pack(expand=1, fill=Tkinter.BOTH)
        self.inputTextPort.pack(expand=1, fill=Tkinter.BOTH)
        self.frame[1].pack(expand=1, fill=Tkinter.BOTH)
        '''

        #frame2
        #显示消息Text右边的滚动条
        self.chatTextScrollBar = Tkinter.Scrollbar(self.frame[2])
        self.chatTextScrollBar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        #显示消息Text，并绑定上面的滚动条
        #本来应该相互绑定，但实际运行时，滑动条没有绑定列表框
        self.chatText = Tkinter.Listbox(self.frame[2], width=80, height=18)
        self.chatText['yscrollcommand'] = self.chatTextScrollBar.set
        self.chatText.pack(expand=1, side=Tkinter.LEFT, fill=Tkinter.BOTH)
        #self.chatTextScrollBar['command'] = self.chatText.yview()
        self.frame[2].pack(fill=Tkinter.BOTH)

        #frame3
        #标签，创建高度为2的空白区区分ListBox和Text
        label = Tkinter.Label(self.frame[3], height=2)
        label.pack(fill=Tkinter.BOTH)
        self.frame[3].pack(fill=Tkinter.BOTH)

        #frame4
        #输入消息Text的滚动条
        self.inputTextScrollBar = Tkinter.Scrollbar(self.frame[4])
        self.inputTextScrollBar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        #输入消息Text，并与滚动条绑定
        #常用字体元组('Arial',('Courier New',),('Comic Sans MS',),'Fixdsys',('MS Sans Serif',),('MS Serif',),'Symbol','System',('Times New Roman',),'Verdana')
        ft4 = tkFont.Font(family='Fixdays', size=11)
        self.inputText = Tkinter.Text(self.frame[4], width=80, height=8, font=ft4)
        self.inputText['yscrollcommand'] = self.inputTextScrollBar.set
        self.inputText.pack(expand=1, fill=Tkinter.BOTH)
        #self.inputTextScrollBar['command'] = self.chatText.yview()
        self.frame[4].pack(fill=Tkinter.BOTH)

        #frame5
        #发送消息按钮
        self.sendButton = Tkinter.Button(self.frame[5], text=' 发 送 ', width=10, command=self.ManualMessage)#setReplyStatus)#发送按钮的事件调用设置回复方式函数
        self.sendButton.pack(expand=1, side=Tkinter.BOTTOM and Tkinter.RIGHT, padx=25, pady=5)

        #关闭按钮
        self.closeButton = Tkinter.Button(self.frame[5], text=' 关 闭 ', width=10, command=self.close)
        self.closeButton.pack(expand=1, side=Tkinter.RIGHT, padx=25, pady=5)
        self.frame[5].pack(expand=1, fill=Tkinter.BOTH)

        '''
        def showCheckButton1Varialbe(self):
            return self.CheckButton1.variable.get()
        def showCheckButton2Varialbe(self):
            return self.CheckButton2.variable.get()
        '''

    #接收消息并显示
    def receiveMessage(self):
        global receiveMsg
        #建立Socket连接

        try:
            self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#建立socket，参数为ipv4，TCP，另一个参数默认为1.
            self.serverSock.bind((self.Ip, self.Port))
            self.serverSock.listen(15)
            self.buffer = 1024
            self.chatText.insert(Tkinter.END, '服务器已经就绪......')
        except:
            self.flag = False
            self.chatText.insert(Tkinter.END,'服务器端建立连接错误，请检查端口和ip是否可用......')

        try:
            while True:
                #循环接受客户端的连接请求
                self.connection, self.address = self.serverSock.accept()
                self.flag = True
                while True:
                    #循环接收客户端发送的消息
                    self.clientMsg = self.connection.recv(self.buffer)
                    if not self.clientMsg:
                        #当接受到的clientMsg为空就跳出循环，出现过卡死状态
                        continue
                        #可以讲下三次握手：客-》服；服-》客；客-》服
                    elif self.clientMsg == 'Y':
                        self.chatText.insert(Tkinter.END, '服务器端已经与客户端建立连接......')
                        self.connection.send('Y')
                    elif self.clientMsg == 'N':
                        self.chatText.insert(Tkinter.END, '服务器端与客户端建立连接失败......')
                        self.connection.send('N')
                    else:
                        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.chatText.insert(Tkinter.END, '客户端 ' + theTime + ' 说：\n')
                        self.chatText.insert(Tkinter.END, '  ' + self.clientMsg)
                        #self.chatText.insert(Tkinter.END, type(self.clientMsg))
                        try:
                            receiveMsg = self.clientMsg
                        except:
                            print "Error"
                        try:
                            self.setReplyStatus()
                        except:
                            self.chatText.insert(Tkinter.END, '回复方式函数错误......')
        except:
            self.chatText.insert(Tkinter.END, '连接错误......')


    #判断回复方式
    def setReplyStatus(self):
        global replyStatus
        global receiveMsg
        #regard the num as 4,2,1,and add it to replyStatus
        if self.CheckVar1.get()==1 and self.CheckVar2.get()==0 and self.CheckVar3.get()==0:
            self.replyStatus=7
            #此处删除函数的原因是，已经设计“发送”按钮的command调用了ManualMessage，所以在此处定义则调用了两次函数，而这里的这个返回空
            #self.ManualMessage()
        #数据库回复
        elif self.CheckVar1.get()==0 and self.CheckVar2.get()==1 and self.CheckVar3.get()==0:
            self.replyStatus=2
            try:
                dataInfo=self.DatabaseInformation()
                print "dataInfo:",dataInfo
                #输入hi时，下面的语句访问错误
                try:
                    self.DatabaseQuestion()
                except:
                    print "hahe181"
                    print "dataQues:",dataQues
                if dataInfo==None and dataQues is not None:

                    self.DatabaseQuestion()
                elif dataInfo==None and dataQues==None:
                    self.chatText.insert(Tkinter.END, '无法匹配数据库信息，请手动回复')
                    self.ManualMessage()
                elif dataInfo is not None and dataQues is None:
                    self.DatabaseInformation()
                #默认两表不存在交集，所以这部分为空
                else:
                    pass
            except:
                pass#self.chatText.insert(Tkinter.END, '数据库回复错误')


        elif self.CheckVar1.get()==0 and self.CheckVar2.get()==0 and self.CheckVar3.get()==1:
            self.replyStatus=1
            self.TuringMessage()


        #数据库+图灵回复
        elif self.CheckVar2.get()==1 and self.CheckVar3.get()==1:
            self.reply=3
            try:
                self.DatabaseInformation()
                if self.DatabaseInformation()==None:
                    self.DatabaseQuestion()
                    if self.DatabaseQuestion()==None:
                        self.TuringMessage()
                        if self.TuringMessage()==None:
                            self.chatText.insert(Tkinter.END, '无法匹配数据库信息，请手动回复')
                            self.ManualMessage()
                    else:
                        self.DatabaseQuestion()
                else:
                    self.DatabaseInformation()
            except:
                self.chatText.insert(Tkinter.END, '数据库+图灵回复错误')

        elif self.CheckVar1.get()==1 and self.CheckVar2.get()==0 and self.CheckVar3.get()==1:
            self.replyStatus=1
            self.TuringMessage()
        elif self.CheckVar1.get()==1 and self.CheckVar2.get()==1 and self.CheckVar3.get()==0:
            self.replyStatus=2
            self.DatabaseInformation()
            self.DatabaseQuestion()
        else:
            #格式化当前的时间
            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
            self.chatText.insert(Tkinter.END,'  ' + '请选择一种回复方式，选择两种以上都变为数据库和图灵自动回复（目前状态）' + '\n')
            #自动切换为011或者111状态
            '''
            #为什么这个也错？暂时放弃
            self.CheckVar2.get()==1
            self.CheckVar3.get()==1
            self.setReplyStatus()
            '''
            '''
            #为什么提示database（）访问有误，global receiveMsg没有定义？
            self.reply=3
            if self.DatabaseMessage()==None:
                if self.TuringMessage()==None:
                    theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                    self.chatText.insert(Tkinter.END,'  ' + '未能成功匹配，请手动输入回复信息' + '\n')
                    self.ManualMessage()
                else:
                    self.TuringMessage()
            else:
                self.DatabaseMessage()
            '''


    '''
    #通过判断回复方式得到将要执行的回复语句，并由此改变replyStatus的值，再由此函数充当此button的commond函数。暂时放弃。
    def setSendButtonStyle(self):
        if self.replyStatus==7:
            self.ManualMessage()
        elif self.replyStatus==:
            self.ManualMessage()
    '''

    #获取图灵消息
    def TuringMessage(self):
        #try:
        #抓取turing的回复
        global receiveMsg
        global string
        #self.chatText.insert(Tkinter.END, "Hello, I'm Turing. Enter bye to quit.")
        TuringQuestion = receiveMsg.encode('utf-8')#.decode('gb18030')
        try:
            TuringQ = "http://www.tuling123.com/openapi/api?key=dcc40d6323b576076c3005043aaba756&info=%s" %(TuringQuestion)
        except:
            self.chatText.insert(Tkinter.END, "无法访问图灵数据库1，暂时将调用手动回复，请输入......")
            self.manualMessage()
        #print 11111
        try:
            TuringRequest = urllib2.Request(TuringQ)
            print 11111
        except:
            self.chatText.insert(Tkinter.END, "图灵数据库提交数据出错2，暂时将调用手动回复，请输入......")
            self.manualMessage()
        #print 22222
        try:
            TuringResponse = urllib2.urlopen(TuringRequest)
            print 22222
        except:
            self.chatText.insert(Tkinter.END, "获取图灵数据库数据错误3，暂时将调用手动回复，请输入......")
            self.manualMessage()
        TuringAnswer= TuringResponse.read().decode('utf-8')#.encode('gb18030')
        #print 33333
        try:
            #从图灵获取的数据是字符串（字典格式的），转化成字典，并提取text对应的字符串
            string = eval(TuringAnswer)["text"]
            print 33333

        except:
            self.chatText.insert(Tkinter.END, "图灵数据库数据转换错误4，无法输出，暂时将调用手动回复，请输入......")
            self.manualMessage()
        #print 44444
        #if self.flag == True:
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
        self.chatText.insert(Tkinter.END,'  ' + string + '\n')
        if self.flag == True:
            self.connection.send(string)
        else:
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')
        #except:
        #return None

    #获取手动输入信息
    def ManualMessage(self):
        message = self.inputText.get('1.0',Tkinter.END)
        #格式化当前的时间
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
        self.chatText.insert(Tkinter.END,'  ' + message + '\n')
        if self.flag == True:
            #将消息发送到客户端
            self.connection.send(message)
        else:
            #Socket连接没有建立，提示用户
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')
        #清空用户在Text中输入的消息
        self.inputText.delete(0.0,message.__len__()-1.0)
        '''
        #手动回复信息，得到用户在Text中输入的消息
        #这个1.0使得get两次，第一次是未输入的情况，get了空，第二次get了输入的字符串
        string = self.inputText.get('1.0',Tkinter.END)
        print "string:",string
        if string is None:
            pass
        elif self.flag == True and string is not None:
            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
            print 112
            self.chatText.insert(Tkinter.END,string)
            print 123
            self.connection.send(string)
            print 124
        else:
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')
        #清空用户在Text中输入的消息
        self.inputText.delete(0.0,message.__len__()-1.0)
        '''

    #--------------------------------------------------------------
    #数据库回复对话信息
    def DatabaseQuestion(self):
        global string
        try:
            #问题出在receiveMsg上!!!
            print 1
            global receiveMsg
            print receiveMsg.strip()
            try:
                conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='n5252n59',db='python',charset='utf8')
            except:
                self.chatText.insert(Tkinter.END, "数据库连接错误，请检查数据库配置")
            with conn:
                cur = conn.cursor()
                sql = "SELECT * from QuestionAnswerInformation WHERE Question LIKE %s"
                #最痛苦的原来是receiveMsg左右各有一个空格，使用strip()消去，就成了正常字符串
                cur.execute(sql,(receiveMsg.strip(),))
                try:
                    pass
                    #cur.execute(sql,(receiveMsg,))
                    #self.chatText.insert(Tkinter.END, "ha311")
                except:
                    self.chatText.insert(Tkinter.END, "数据库语句载入错误，请检查数据库配置")
                try:
                    results=cur.fetchall()
                    #!!!这里返回为空！！！？？？
                    #print 'results:',results
                except:
                    self.chatText.insert(Tkinter.END, "fetch Error 317")
                try:
                    question=results[0][1]
                except:
                    #！！！这句在输入信息查询时会输出，报错？？？
                    #self.chatText.insert(Tkinter.END, "fetch Error 362")
                    pass
                #self.chatText.insert(Tkinter.END, question)

                #print question
                answer=results[0][2]

                #self.chatText.insert(Tkinter.END, answer)
                #print "answer:",answer
                LinkToNum=results[0][3]
                #print "LinkToNum:",LinkToNum
                LinkToString=results[0][4]
                #print "LinkToString:",LinkToString

                cur.close()

                '''
                #载入随机数，判断通过本词条回复，还是相似词条（可链接到的）回复
                randomReply=random.randrange(0,2)
                #print randomReply
                if randomReply is not 0 and answer is not None:
                    string = "%s：%s。" %(question,answer)
                    print string
                else:
                '''
                #！！！3个数据8种回复方式
                #(任，空，空)当首次查询的结果为空时，创建另一个游标，获取linkToNum，并通过Num查找链接向的词条
                if LinkToNum is None and LinkToString is None:
                    #！！！这里需要对确切信息和相似信息坐下处理（LIKE和=的区别）
                    #string = "%s：%s。" %(question,answer)
                    #print "您想问的是这个吗？"
                    if answer is not None:
                        string = "%s。" %(answer)
                        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                        self.chatText.insert(Tkinter.END, string)
                    else:
                        self.chatText.insert(Tkinter.END, "return None from the database,Please use the ManualMessage")

                #（任，非，非）
                elif LinkToNum is not None and LinkToString is not None:
                    self.chatText.insert(Tkinter.END, "数据库信息输出错误，不建议链接到字符串和链接到编号同时存在，请检查数据库")

                #（任，非，空）
                elif LinkToNum is not None and LinkToString is None:
                    if answer is None:
                        #直接查找链接到的词条，和下面else后的代码一样，但是写函数就不方便了，所以写两个
                        try:
                            curNum = conn.cursor()
                            sqlLinkToNum = "SELECT * from QuestionAnswerInformation WHERE Num = %s"
                        except:
                            self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库1")
                        try:
                            curNum.execute(sqlLinkToNum,(LinkToNum,))
                        except:
                            self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库2")
                        try:
                            resultsNum=curNum.fetchall()
                            string = "%s：%s。" %(resultsNum[0][1],resultsNum[0][2])
                            if resultsNum[0][2] is not None:
                                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                                self.chatText.insert(Tkinter.END, "您想问的是这个吗？")
                                self.chatText.insert(Tkinter.END, string)
                            else:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库3")
                        except:
                            self.chatText.insert(Tkinter.END, "return None from the database,Please use the ManualMessage")
                        curNum.close()

                    elif answer is not None:
                        #(非，非，空)(用例是输入hi)载入随机数，判断通过本词条回复，还是相似词条（可链接到的）回复
                        randomReply=random.randrange(0,2)
                        #曾经随机数出过问题，通过print检验没有问题啊
                        #print randomReply
                        if randomReply is not 0:
                            #string = "%s：%s。" %(question,answer)
                            string = "%s。" %(answer)
                            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                            self.chatText.insert(Tkinter.END, string)
                        else:
                            #执行LinkToNum链接到的词条
                            try:
                                curNum = conn.cursor()
                                sqlLinkToNum = "SELECT * from QuestionAnswerInformation WHERE Num = %s"
                            except:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库1")
                            try:
                                curNum.execute(sqlLinkToNum,(LinkToNum,))
                            except:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库2")
                            try:
                                resultsNum=curNum.fetchall()
                                string = "%s。" %(resultsNum[0][2])
                                #string = "%s：%s。" %(resultsNum[0][1],resultsNum[0][2])
                                if resultsNum[0][2] is not None:
                                    #print "您想问的是这个吗？"
                                    self.chatText.insert(Tkinter.END, string)
                                else:
                                    self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库3")
                            except:
                                self.chatText.insert(Tkinter.END, "return None from the database,Please use the ManualMessage")
                            curNum.close()


                #（任，空，非）链接到字符串
                elif LinkToNum is None and LinkToString is not None:
                    if answer is None:
                        try:
                            curString = conn.cursor()
                            sqlLinkToString = "SELECT * from QuestionAnswerInformation WHERE Question = %s"
                        except:
                            self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库1")

                        curString.execute(sqlLinkToString,(LinkToString,))
                        try:
                            resultsString=curString.fetchall()
                            string = "%s：%s。" %(resultsString[0][1],resultsString[0][2])
                            if resultsString[0][2] is not None:
                                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                                self.chatText.insert(Tkinter.END, "您想问的是这个吗？")
                                self.chatText.insert(Tkinter.END, string)
                            else:
                                self.chatText.insert(Tkinter.END, "return None from the database,Please use the ManualMessage")
                        except:
                            self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库2")
                        curString.close()
                    elif answer is not None:
                        randomReply=random.randrange(0,2)
                        #print randomReply
                        if randomReply is not 0:

                            #string = "%s：%s。" %(question,answer)
                            string = "%s。" %(answer)
                            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                            self.chatText.insert(Tkinter.END, string)
                        else:
                            try:
                                curString = conn.cursor()
                                sqlLinkToString = "SELECT * from QuestionAnswerInformation WHERE Question = %s"
                            except:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库1")
                            try:
                                curString.execute(sqlLinkToString,(LinkToString,))
                            except:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库2")

                            try:
                                resultsString=curString.fetchall()
                                string = "%s：%s。" %(resultsString[0][1],resultsString[0][2])
                            except:
                                self.chatText.insert(Tkinter.END, "数据库信息输出错误，请检查数据库3")
                            if answer is not None:
                                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
                                self.chatText.insert(Tkinter.END, "您想问的是这个吗？")
                                self.chatText.insert(Tkinter.END, string)
                                curString.close()
                            else:
                                self.chatText.insert(Tkinter.END, "return None from the database,Please use the ManualMessage")
                                curString.close()

                #默认linkToString和LinkToNum不能同时不为空，可以同时为空，或者一个为空
                #if self.flag == True and string is not None:
                if string is not None:
                    self.connection.send(string)
                    #return string
                else:
                    self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')
        except:
            return None
    #--------------------------------------------------------------


    #数据库回复商品信息
    def DatabaseInformation(self):
        '''
        global receiveMsg
        print receiveMsg.strip()
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='n5252n59',db='python',charset='utf8')
        except:
            self.chatText.insert(Tkinter.END, "数据库连接错误，请检查数据库配置")
        with conn:
            cur = conn.cursor()
            sql = "SELECT * from QuestionAnswerInformation WHERE Question LIKE %s"
            #最痛苦的原来是receiveMsg左右各有一个空格，使用strip()消去，就成了正常字符串
            cur.execute(sql,(receiveMsg.strip(),))
            try:
                pass
                #cur.execute(sql,(receiveMsg,))
                #self.chatText.insert(Tkinter.END, "ha311")
            except:
                self.chatText.insert(Tkinter.END, "数据库语句载入错误，请检查数据库配置")
            try:
                results=cur.fetchall()
                #!!!这里返回为空！！！？？？
                print 'results:',results
        '''
        #import MySQLdb
        try:
            global receiveMsg
            #print "receiveMsg:",receiveMsg
            #print "receiveMsg.strip():",receiveMsg.strip()
            #global message
            #theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            #self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
            try:
                conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='n5252n59',db='python',charset='utf8')
            except:
                self.chatText.insert(Tkinter.END, "数据库连接错误，请检查数据库配置")
            with conn:
                cur = conn.cursor()
                sql="SELECT * from LeatherShoesInformation WHERE ShoesName LIKE %s"
                cur.execute(sql,(receiveMsg.strip(),))
            try:
                results=cur.fetchall()
                print results
            except:
                print "error"
            #cur.execute(sql,(receiveMsg,))
            #lineNum = int(cur.rowcount)
            #databaseReturn = cur.fetchone()[lineNum-1]
            #print databaseReturn

            string1 = "我猜，您正考虑的就是这款皮鞋吧："
            string2 = "%s,原价：%s,打折后只有：%s。" %(results[0][2],results[0][3],results[0][4])
            string3 = "这款鞋是（%s),(%s)的。" %(results[0][7],results[0][8])
            string4 = "另外，这款鞋是卖家评价%s,%s的优质皮鞋。" %(results[0][12],results[0][10])
            string5 = "如果您想购买这双皮鞋，我们还将赠送您%s。我们建议您,%s。" %(results[0][11],results[0][13])
            string = string1+string2+string3+string4+string5

            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
            self.chatText.insert(Tkinter.END,string1)
            self.chatText.insert(Tkinter.END,string2)
            self.chatText.insert(Tkinter.END,string3)
            self.chatText.insert(Tkinter.END,string4)
            self.chatText.insert(Tkinter.END,string5)
            cur.close()
            #if self.flag == True:
            #self.sendMessage()
            #这一行如果调用sendMessage()，将只输出一行
            if self.flag == True:
                self.connection.send(string)
            else:
                self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')

                #self.connection.send(string2)
                #self.connection.send(string3)
                #self.connection.send(string4)
                #self.connection.send(string5)
        except:
            return

    #6月7日决定注销这段代码，将输出放在函数中进行
    #发送消息，只供manual和turing调用，database的发送方式还没定
    '''
    def sendMessage(self):
        global message
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.chatText.insert(Tkinter.END, '服务器 ' + theTime +' 说：\n')
        self.chatText.insert(Tkinter.END,'  ' + message + '\n')
        if self.flag == True:
            self.connection.send(message)
        else:
            self.chatText.insert(Tkinter.END,'您还未与客户端建立连接，客户端无法收到您的消息\n')
    '''


    #关闭消息窗口并退出
    def close(self):
        sys.exit()

    #启动线程接收客户端的消息
    def startNewThread(self):
        #启动一个新线程来接收客户端的消息
        #thread.start_new_thread(function,args[,kwargs])函数原型，
        #其中function参数是将要调用的线程函数，args是传递给线程函数的参数，它必须是个元组类型，而kwargs是可选的参数
        #receiveMessage函数不需要参数，就传一个空元组
        thread.start_new_thread(self.receiveMessage, ())
        #thread.start_new_thread(self.setReplyStatus, ())

def main():
    server = Server()
    server.startNewThread()
    server.setReplyStatus()
    server.root.mainloop()


if __name__ == '__main__':
    main()
