#!/usr/bin/python
# Bu program bir ozgur yazilim urunudur. Bu programi GNU Genel Kamu
# Lisansi aldinta dilediginiz gibi cogaltip, degistirip kullanabilirsiniz
# tumunu yada parcalarini arkadaslariniz ile paylasabilirsiniz.
# WiiMote ve Wii Nintendo firmasinin tescilli urunudur.

import random
import cwiid
import time
import sys

"""
Bluetooth destekli bir linux sistem uzerinde Wii uzaktan kumandasi 
ile oynanan sayi bulmaca oyunu. cwiid kutuphanesi icin bkz: 
http://talk.maemo.org/showthread.php?t=60178
Windowze/mac sistemce cwiid nin destegi varsa denenebilir
"""

wm = None

#    WiiMote ile baglanti kuralim. Baglanti saglanirsa
#    WiiMote 'un A-B tusalarini ve asagi yukari sensorunu aktif edelim
#    sonra 1. isigini yakalim
def connect_mote():
    global wm
    print "Lutfen Wiimote uzerine 1 ve 2 tusuna ayni anda basiniz"
    try:
        wm = cwiid.Wiimote()
        wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
        wm.led = 1
        print "Wiimote baglantisi saglandi"
    except RuntimeError:
        print "wiimote cihazina baglanilamadi"

    return wm

def sayi_al(prompt):
    try:
        tahmin=int(raw_input(prompt))
    except ValueError:
        tahmin =0
    return tahmin

# Kotuce bir ansi-terminal hack. 
# http://stackoverflow.com/questions/7392779/is-it-possible-to-print-a-string-at-a-certain-screen-position-inside-idle
def print_there(x, y, text,stat):
    output = "[ Tahmin: %d ] [%d] " % (text, stat)
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, output))
    sys.stdout.flush()

# BTN_A ya basilana kadar dongude kalalim. wm.state['acc'][1] bize WiiMote
# yonu yukarda yada asagida durumuna gore tahminimizi artiracak yada azaltacak
def wm_sayi_al(wm,tahmin,max_tahmin):

    while not wm.state['buttons'] & cwiid.BTN_A:
        accel = wm.state['acc'][1]
        # Yaklasik olarak accel > 128 'k ise WiiMote asagi dogru 
        # cevrilmis, accel < 128 ise asagi dogru bakiyor diyebiliriz.
        # TODO buraya daha iyi bir kalibrasyon yazmak gerekiyor
        var = int ((129 - accel) / 6)

        # WiiMode dan gelen hesaplamanin oyun limitlerini asmasini engelleyelim
        if 0 <= tahmin + var <= max_tahmin: 
            tahmin += var
        
        print_there(100,1,tahmin,var)
        time.sleep(.2)

    time.sleep(.4)
    return tahmin

#  max_tahmin ile 0 arasinda Wiimote ile gonderdiginiz tahminler
#  burada kontrol ediliyor
def sayi_oyunu(max_tahmin,wm):

    deneme=0
    tahmin =(0 + max_tahmin)/2
    gizlisayi = random.randint(1, max_tahmin)

    print "0 ve %s arasinda bir sayi tuttum. Hadi tahmin edin" % max_tahmin

    start_time = time.time()

    while True:
        deneme +=1
        tahmin = wm_sayi_al(wm,tahmin,max_tahmin)
        #tahmin=sayi_al("[%s] Tahmininizi nedir? :" % deneme )

        print "[%d] Tahmininiz: %d" % (deneme,tahmin),

        if tahmin == gizlisayi: 
            print( "Bravo %s denemede ve %s saniye surede buldunuz") % (deneme, (time.time() - start_time) )
            break
        elif tahmin == 0:
            print "0 dan buyuk bir sayi tahmin etmeniz lazim"
        elif tahmin < gizlisayi: 
            print "Benim tuttugum sayi daha buyuk"
        elif tahmin > gizlisayi: 
            print "Benim tuttugum sayi daha kucuk"

def main():
    global wm
    print "Sayi bulmaca oyununa hosgeldiniz."

    # WiiMote 'a baglanana kadar deneyelim 
    while not wm:
        wm=connect_mote()
    
    max_tahmin = sayi_al("Ust Limitiniz nedir? [100]:")
    if max_tahmin == 0: max_tahmin = 100
    print """
             Tahmini yapmak icin WiiMote 'u yukari yada asagi cevirin
             Kumandayi yukari dogru kaldirdiginizda tahmin artacak
             asagi cevirdiginizde azalacaktir.
             Dogru tahmine geldiginizda kumandada A tusuna basiniz\n\n"""
    
    sayi_oyunu(max_tahmin,wm)

    kontrol = raw_input("Bir daha oynamak ister misiniz? [E/H]:")
    if kontrol == 'E' or kontrol == 'e': main()

# Boilerplate
if __name__ == '__main__':
    main()
            
