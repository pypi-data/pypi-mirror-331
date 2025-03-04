import os
from argostranslate import translate
from logger import log_info, log_error
from colorama import Fore, Style

# Çeviri ve kayıt işlemleri
class AutoTranslate:
    def __init__(self):
        log_info("Çeviri sistemi başlatıldı.")

    def translate_text(self, text, int_lang, out_lang):
        try:
            log_info(f"Çeviri başlıyor: {int_lang.upper()} → {out_lang.upper()}")
            translated_text = translate.translate(text, int_lang, out_lang)
            log_info(f"Çeviri tamamlandı: {translated_text}")

            # Konsola yazdırma
            print(Fore.CYAN + f"\n{int_lang.upper()}: {text}" + Style.RESET_ALL)
            print(Fore.GREEN + f"{out_lang.upper()}: {translated_text}\n" + Style.RESET_ALL)

            # TXT'ye kaydetme
            self.save_translation(int_lang, out_lang, text, translated_text)

            return translated_text
        except Exception as e:
            log_error(f"Çeviri hatası: {str(e)}")
            return None

    def save_translation(self, int_lang, out_lang, text, translated_text):
        filename = "lenuxtranslate_out.txt"
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"{int_lang.upper()} - {out_lang.upper()}\n")
            file.write(f"{int_lang.upper()}: {text}\n")
            file.write(f"{out_lang.upper()}: {translated_text}\n")
            file.write("="*50 + "\n")
        log_info(f"Çeviri kaydedildi: {filename}")

# Kullanıcıdan çeviri iste
def main():
    translator = AutoTranslate()

    while True:
        print(Fore.YELLOW + "\nÇeviri yapmak istediğiniz dilleri seçiniz:" + Style.RESET_ALL)
        int_lang = input("Kaynak Dil (Örn: tr): ").strip().lower()
        out_lang = input("Hedef Dil (Örn: en): ").strip().lower()
        text = input(f"{int_lang.upper()} dilinde çevrilecek metni giriniz: ").strip()

        if text:
            translator.translate_text(text, int_lang, out_lang)

        # Tekrar çeviri isteği
        again = input(Fore.MAGENTA + "\nBaşka bir çeviri yapmak ister misiniz? (evet/hayır): " + Style.RESET_ALL).strip().lower()
        if again != "evet":
            print(Fore.RED + "\nÇeviri programı sonlandırılıyor...\n" + Style.RESET_ALL)
            break
        else:
            os.system("cls" if os.name == "nt" else "clear")  # Ekranı temizle

if __name__ == "__main__":
    main()
