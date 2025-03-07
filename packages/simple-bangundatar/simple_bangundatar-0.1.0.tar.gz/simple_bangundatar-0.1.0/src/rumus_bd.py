class Rumus:
    @staticmethod
    def tambah(a, b):
        return a + b
    
    @staticmethod
    def kurang(a, b):
        return a - b
    
    @staticmethod
    def kali(a, b):
        return a * b
    
    @staticmethod
    def bagi(a, b):
        return a / b

    @staticmethod
    def pangkat(a, b):
        return a ** b

class Persegi_Panjang:
    def __init__(self, panjang, lebar):
        self.panjang = panjang
        self.lebar = lebar
        self.luas = 0
        self.keliling = 0
    

    def getLuas(self):
        self.luas = Rumus.kali(self.panjang, self.lebar)

    
    def getKeliling(self):
        self.keliling = Rumus.kali(2, Rumus.tambah(self.panjang, self.lebar))

    
class Persegi:
    def __init__(self, sisi):
        self.sisi = sisi
        self.luas = 0
        self.keliling = 0

    def getLuas(self):
        self.luas = Rumus.pangkat(self.sisi, 2)

    def getKeliling(self):
        self.keliling = Rumus.kali(self.sisi, 4)

class Segitiga_SamaSisi:
    def __init__(self, sisi, tinggi):
        self.sisi = sisi
        self.alas = sisi
        self.tinggi = tinggi
        self.luas = 0
        self.keliling = 0

    def getLuas(self):
        self.luas = Rumus.kali(Rumus.bagi(1,2), Rumus.kali(self.alas, self.tinggi))
    
    def getKeliling(self):
        self.keliling = Rumus.kali(self.sisi, 3)

    