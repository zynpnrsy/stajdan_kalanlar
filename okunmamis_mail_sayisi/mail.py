import imaplib
import getpass
#from win10toast import ToastNotifier // pythonda win10toast sürüm farklılığından çalışmayabilir
from win10toast_click import ToastNotifier 

def get_unread_mail_count(email,password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email , password)
    mail.select("inbox")

    status , response = mail.search(None , 'X-GM-RAW "label:inbox is:unread"') # "UNSEEN"
    unread_message_num = response[0].split()
    return len(unread_message_num)


def main():
    email = "zpinarsoy@gmail.com"
    password2 = input("Uygulama Sifresi:") 

    ##password2 = getpass.getpass("Uygulama Sifresi:")  //Şifre görünmeden alınıyor
    ##sifre = input("Uygulama Şifresi: ")  // Şifre görünür şekilde alınıyor
    print(f"Girilen şifre: {password2}")
        

    try:
        unread_count =get_unread_mail_count(email,password2)
        print (f"Okunmamış Mail Sayısı: {unread_count}")
        print("Giriş başarılı!")

        notifier = ToastNotifier()
        notifier.show_toast("Gmail Bildirimi", f"Okunmamış mail sayısı: {unread_count}", duration=10)

    except Exception as Hata:
        print("Hata var:" ,Hata)

if __name__== "__main__" :
    main()
            



