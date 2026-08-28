import time
import requests
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException
)

import data


# ============================================================
# CONFIG
# ============================================================

URL = "https://www.kageherostudio.com/event/?event=daily"

EMAIL = data.EMAIL
PASSWORD = data.PASSWORD

DISCORD_WEBHOOK = data.DISCORD_WEBHOOK

CLAIM_HOUR = data.CLAIM_HOUR
CLAIM_MINUTE = data.CLAIM_MINUTE

TARGET_SERVER = str(data.SERVER)

WAIT_TIMEOUT = 20
CLAIM_WAIT = 10


# ============================================================
# GLOBAL DRIVER
# ============================================================

driver = None
wait = None


# ============================================================
# START CHROME
# ============================================================

def start_browser():

    global driver
    global wait

    print()
    print("================================")
    print("START CHROME")
    print("================================")

    options = Options()

    # HEADLESS
    options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Stabilitas
    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(
        driver,
        WAIT_TIMEOUT
    )

    print("Chrome headless berhasil dibuka.")


# ============================================================
# CLOSE CHROME
# ============================================================

def close_browser():

    global driver
    global wait

    print()
    print("================================")
    print("MENUTUP CHROME")
    print("================================")

    try:

        if driver is not None:
            driver.quit()

            print("Chrome ditutup.")

    except Exception as e:

        print(
            f"Gagal menutup Chrome: {e}"
        )

    driver = None
    wait = None


# ============================================================
# SCREENSHOT
# ============================================================

def screenshot(filename):

    try:

        if driver is not None:

            driver.save_screenshot(
                filename
            )

            print(
                f"Screenshot disimpan: {filename}"
            )

    except Exception:
        pass


# ============================================================
# DISCORD WEBHOOK
# ============================================================

def send_discord(message):

    print()
    print("================================")
    print("DISCORD WEBHOOK")
    print("================================")

    try:

        response = requests.post(
            DISCORD_WEBHOOK,
            json={
                "content": message
            },
            timeout=15
        )

        if response.status_code in [200, 204]:

            print(
                "Discord webhook: BERHASIL"
            )

            return True

        print(
            f"Discord webhook: GAGAL "
            f"(HTTP {response.status_code})"
        )

    except Exception as e:

        print(
            f"Discord webhook error: {e}"
        )

    return False


# ============================================================
# LOGIN
# ============================================================

def login():

    print()
    print("================================")
    print("LOGIN")
    print("================================")

    try:

        # ----------------------------------------------------
        # Cek apakah sudah login
        # ----------------------------------------------------

        existing_user = driver.find_elements(
            By.CSS_SELECTOR,
            ".userid-daily"
        )

        if existing_user:

            print(
                "Session login masih aktif."
            )

            return True

        # ----------------------------------------------------
        # Cari LOGIN
        # ----------------------------------------------------

        print(
            "Mencari tombol LOGIN..."
        )

        login_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".loginMethod"
                )
            )
        )

        login_button.click()

        print(
            "LOGIN diklik."
        )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        email_input = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#form-login input[name='txtuserid']"
                )
            )
        )

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        password_input = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#form-login input[name='txtpassword']"
                )
            )
        )

        email_input.clear()
        email_input.send_keys(
            EMAIL
        )

        password_input.clear()
        password_input.send_keys(
            PASSWORD
        )

        print(
            "Credential diisi."
        )

        # ----------------------------------------------------
        # SUBMIT LOGIN
        # ----------------------------------------------------

        login_submit = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "form-login-btnSubmit"
                )
            )
        )

        login_submit.click()

        print(
            "SUBMIT LOGIN diklik."
        )

        print(
            "Menunggu login..."
        )

        time.sleep(5)

        # ----------------------------------------------------
        # Buka kembali halaman daily
        # ----------------------------------------------------

        driver.get(URL)

        time.sleep(3)

        # ----------------------------------------------------
        # Cek login
        # ----------------------------------------------------

        userid = driver.find_elements(
            By.CSS_SELECTOR,
            ".userid-daily"
        )

        if userid:

            print()
            print("================================")
            print("HASIL LOGIN")
            print("================================")

            print(
                f"URL: {driver.current_url}"
            )

            print(
                "STATUS: LOGIN BERHASIL"
            )

            return True

        print(
            "LOGIN GAGAL."
        )

        return False

    except Exception as e:

        print()
        print("LOGIN ERROR")

        print(
            type(e).__name__
        )

        print(e)

        screenshot(
            "error_login.png"
        )

        return False


# ============================================================
# FIND ACTIVE REWARD
# ============================================================

def find_active_reward():

    print()
    print("================================")
    print("MENCARI REWARD AKTIF")
    print("================================")

    try:

        rewards = driver.find_elements(
            By.CSS_SELECTOR,
            ".dailyClaim"
        )

        print(
            f"Jumlah reward ditemukan: "
            f"{len(rewards)}"
        )

        for index in range(
            len(rewards)
        ):

            try:

                # Ambil ulang element
                current_rewards = driver.find_elements(
                    By.CSS_SELECTOR,
                    ".dailyClaim"
                )

                reward = current_rewards[
                    index
                ]

                day = reward.find_element(
                    By.CSS_SELECTOR,
                    ".reward-point"
                ).text.strip()

                name = reward.get_attribute(
                    "data-name"
                )

                reward_id = reward.get_attribute(
                    "data-id"
                )

                period = reward.get_attribute(
                    "data-period"
                )

                classes = (
                    reward.get_attribute("class")
                    or ""
                )

                print(
                    f"{day} | "
                    f"{name} | "
                    f"id={reward_id} | "
                    f"class={classes}"
                )

                # ------------------------------------------------
                # AKTIF = TIDAK ADA GRAYSCALE
                # ------------------------------------------------

                if "grayscale" not in classes:

                    print()
                    print(
                        "REWARD AKTIF DITEMUKAN"
                    )

                    print(
                        f"Day    : {day}"
                    )

                    print(
                        f"Nama   : {name}"
                    )

                    print(
                        f"ID     : {reward_id}"
                    )

                    print(
                        f"Period : {period}"
                    )

                    # Simpan DATA, bukan element Selenium
                    return {
                        "day": day,
                        "name": name,
                        "id": reward_id,
                        "period": period
                    }

            except StaleElementReferenceException:

                continue

            except Exception:

                continue

        print()
        print(
            "Tidak ditemukan reward aktif."
        )

        return None

    except Exception as e:

        print(
            f"Gagal membaca reward: {e}"
        )

        return None


# ============================================================
# CLAIM REWARD
# ============================================================

def claim_reward(reward_info):

    print()
    print("================================")
    print("CLAIM REWARD")
    print("================================")

    print(
        f"Day   : {reward_info['day']}"
    )

    print(
        f"Item  : {reward_info['name']}"
    )

    print(
        f"ID    : {reward_info['id']}"
    )

    # ========================================================
    # CARI ULANG REWARD
    # ========================================================

    try:

        rewards = driver.find_elements(
            By.CSS_SELECTOR,
            ".dailyClaim"
        )

        target_reward = None

        for reward in rewards:

            try:

                reward_id = reward.get_attribute(
                    "data-id"
                )

                if reward_id == reward_info["id"]:

                    target_reward = reward

                    break

            except StaleElementReferenceException:

                continue

        if target_reward is None:

            print(
                "Reward target tidak ditemukan."
            )

            return False

        # ====================================================
        # CLICK REWARD
        # ====================================================

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            target_reward
        )

        time.sleep(1)

        print(
            "Klik reward..."
        )

        target_reward.click()

        print(
            "Reward diklik."
        )

    except Exception as e:

        print(
            f"Gagal klik reward: {e}"
        )

        screenshot(
            "error_reward_click.png"
        )

        return False

    # ========================================================
    # PILIH SERVER
    # ========================================================

    print()
    print("================================")
    print("PILIH SERVER")
    print("================================")

    try:

        server_select = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#form-server select[name='selserver']"
                )
            )
        )

        select = Select(
            server_select
        )

        found_server = False

        for option in select.options:

            value = (
                option.get_attribute("value")
            )

            text = option.text.strip()

            print(
                f"Server option: "
                f"value={value} | "
                f"text={text}"
            )

            if value == TARGET_SERVER:

                select.select_by_value(
                    TARGET_SERVER
                )

                print()
                print(
                    f"Server dipilih: {text}"
                )

                found_server = True

                break

        if not found_server:

            print()
            print(
                f"SERVER {TARGET_SERVER} "
                "tidak ditemukan."
            )

            screenshot(
                "error_server.png"
            )

            return False

    except Exception as e:

        print(
            f"Gagal memilih server: {e}"
        )

        screenshot(
            "error_server.png"
        )

        return False

    # ========================================================
    # SUBMIT SERVER
    # ========================================================

    print()
    print("================================")
    print("SUBMIT SERVER")
    print("================================")

    try:

        submit_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "form-server-btnSubmit"
                )
            )
        )

        print(
            "SUBMIT SERVER diklik."
        )

        submit_button.click()

        # ====================================================
        # JAVASCRIPT CONFIRM
        # ====================================================

        try:

            alert = WebDriverWait(
                driver,
                5
            ).until(
                EC.alert_is_present()
            )

            print()
            print("================================")
            print("CONFIRMATION")
            print("================================")

            print(
                alert.text
            )

            alert.accept()

            print(
                "OK diklik."
            )

        except TimeoutException:

            print(
                "Confirmation tidak muncul."
            )

            screenshot(
                "error_confirmation.png"
            )

            return False

    except Exception as e:

        print(
            f"Gagal submit server: {e}"
        )

        screenshot(
            "error_submit.png"
        )

        return False

    # ========================================================
    # TUNGGU GRAYSCALE
    # ========================================================

    print()
    print("================================")
    print("MENUNGGU HASIL CLAIM")
    print("================================")

    print(
        f"Menunggu maksimal "
        f"{CLAIM_WAIT} detik sampai "
        f"reward menjadi disabled..."
    )

    start_time = time.time()

    while (
        time.time() - start_time
        < CLAIM_WAIT
    ):

        time.sleep(1)

        try:

            current_rewards = driver.find_elements(
                By.CSS_SELECTOR,
                ".dailyClaim"
            )

            for current_reward in current_rewards:

                try:

                    current_id = (
                        current_reward
                        .get_attribute("data-id")
                    )

                    if current_id != reward_info["id"]:

                        continue

                    classes = (
                        current_reward
                        .get_attribute("class")
                        or ""
                    )

                    if "grayscale" in classes:

                        print()
                        print(
                            "REWARD BERUBAH "
                            "MENJADI DISABLED."
                        )

                        print(
                            "STATUS: CLAIM BERHASIL"
                        )

                        return True

                except StaleElementReferenceException:

                    continue

        except Exception:

            continue

    # ========================================================
    # FINAL CHECK
    # ========================================================

    print()
    print(
        "Waktu tunggu selesai."
    )

    try:

        driver.refresh()

        time.sleep(3)

        current_rewards = driver.find_elements(
            By.CSS_SELECTOR,
            ".dailyClaim"
        )

        for current_reward in current_rewards:

            try:

                current_id = (
                    current_reward
                    .get_attribute("data-id")
                )

                if current_id != reward_info["id"]:

                    continue

                classes = (
                    current_reward
                    .get_attribute("class")
                    or ""
                )

                if "grayscale" in classes:

                    print(
                        "Reward terdeteksi "
                        "DISABLED setelah refresh."
                    )

                    print(
                        "STATUS: CLAIM BERHASIL"
                    )

                    return True

            except StaleElementReferenceException:

                continue

    except Exception:

        pass

    print()
    print(
        "STATUS: CLAIM TIDAK TERVALIDASI"
    )

    screenshot(
        "claim_not_confirmed.png"
    )

    return False


# ============================================================
# SATU SIKLUS CLAIM
# ============================================================

def run_claim():

    print()
    print("################################")
    print("# MULAI PROSES CLAIM")
    print("################################")

    try:

        start_browser()

        # ----------------------------------------------------
        # Buka website
        # ----------------------------------------------------

        driver.get(URL)

        time.sleep(3)

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        if not login():

            print(
                "LOGIN GAGAL."
            )

            return False

        # ----------------------------------------------------
        # CARI REWARD
        # ----------------------------------------------------

        reward = find_active_reward()

        if reward is None:

            print()
            print(
                "Tidak ada reward aktif."
            )

            return False

        # ----------------------------------------------------
        # CLAIM
        # ----------------------------------------------------

        success = claim_reward(
            reward
        )

        # ----------------------------------------------------
        # DISCORD
        # ----------------------------------------------------

        if success:

            message = (
                "🎁 **NINJA INCOME CLAIM BERHASIL**\n\n"
                f"📅 **{reward['day']}**\n"
                f"🎁 Reward: **{reward['name']}**\n"
                f"🖥️ Server: **Server {TARGET_SERVER}**\n"
                "✅ Status: **Successfully Claimed**"
            )

            send_discord(
                message
            )

            print()
            print(
                "CLAIM SELESAI."
            )

            return True

        print()
        print(
            "Claim gagal / belum terverifikasi."
        )

        return False

    except Exception as e:

        print()
        print("================================")
        print("ERROR PROSES CLAIM")
        print("================================")

        print(
            type(e).__name__
        )

        print(e)

        screenshot(
            "error.png"
        )

        return False

    finally:

        # ====================================================
        # PENTING:
        # Chrome ditutup SETIAP selesai satu siklus.
        # Program Python tetap hidup.
        # ====================================================

        close_browser()


# ============================================================
# GET NEXT SCHEDULE
# ============================================================

def get_next_claim_time():

    now = datetime.now()

    target = now.replace(
        hour=CLAIM_HOUR,
        minute=CLAIM_MINUTE,
        second=0,
        microsecond=0
    )

    if now >= target:

        target += timedelta(
            days=1
        )

    return target


# ============================================================
# WAIT UNTIL SCHEDULE
# ============================================================

def wait_until_schedule():

    target = get_next_claim_time()

    print()
    print("================================")
    print("SCHEDULER")
    print("================================")

    print(
        f"Jadwal berikutnya: "
        f"{target.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print(
        "Menunggu sampai waktu claim..."
    )

    while True:

        now = datetime.now()

        remaining = (
            target - now
        ).total_seconds()

        # ====================================================
        # SUDAH WAKTUNYA
        # ====================================================

        if remaining <= 0:

            print()
            print()
            print("================================")
            print("WAKTU CLAIM TERCAPAI")
            print("================================")

            print(
                f"Sekarang: "
                f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            print(
                "Menjalankan proses claim..."
            )

            return

        # ====================================================
        # COUNTDOWN
        # ====================================================

        hours = int(
            remaining // 3600
        )

        minutes = int(
            (remaining % 3600) // 60
        )

        seconds = int(
            remaining % 60
        )

        print(
            f"\rMenunggu "
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}",
            end="",
            flush=True
        )

        # Maksimal tidur 1 detik
        time.sleep(
            min(1, remaining)
        )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    print()
    print("================================")
    print("NINJA INCOME AUTO CLAIM")
    print("================================")

    print(
        f"Schedule : "
        f"{CLAIM_HOUR:02d}:"
        f"{CLAIM_MINUTE:02d}"
    )

    print(
        f"Server   : Server {TARGET_SERVER}"
    )

    print(
        "Mode     : HEADLESS"
    )

    print()
    print(
        "Program akan berjalan terus."
    )

    print(
        "Tekan CTRL+C untuk berhenti."
    )

    # ========================================================
    # LOOP HARIAN
    # ========================================================

    while True:

        try:

            # ------------------------------------------------
            # 1. Tunggu jadwal
            # ------------------------------------------------

            wait_until_schedule()

            # ------------------------------------------------
            # 2. Jalankan claim
            # ------------------------------------------------

            print()
            print(
                "Memulai proses claim..."
            )

            success = run_claim()

            # ------------------------------------------------
            # 3. Hasil
            # ------------------------------------------------

            print()
            print("================================")
            print("HASIL SIKLUS")
            print("================================")

            if success:

                print(
                    "CLAIM BERHASIL."
                )

                print(
                    "Discord webhook sudah diproses."
                )

            else:

                print(
                    "CLAIM GAGAL / "
                    "TIDAK TERVALIDASI."
                )

            # ------------------------------------------------
            # 4. Jangan claim lagi hari yang sama
            #
            # Tunggu sampai besok.
            # ------------------------------------------------

            next_target = (
                datetime.now()
                .replace(
                    hour=CLAIM_HOUR,
                    minute=CLAIM_MINUTE,
                    second=0,
                    microsecond=0
                )
                + timedelta(days=1)
            )

            print()
            print("================================")
            print("MENUNGGU HARI BERIKUTNYA")
            print("================================")

            print(
                f"Claim berikutnya: "
                f"{next_target.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # ------------------------------------------------
            # Loop kembali ke wait_until_schedule()
            # ------------------------------------------------

        except KeyboardInterrupt:

            print()
            print()
            print("================================")
            print("CTRL+C")
            print("================================")

            print(
                "Program dihentikan oleh user."
            )

            break

        except Exception as e:

            print()
            print("================================")
            print("ERROR MAIN LOOP")
            print("================================")

            print(
                type(e).__name__
            )

            print(e)

            # Pastikan Chrome ditutup
            close_browser()

            print()
            print(
                "Program tetap berjalan."
            )

            print(
                "Akan mencoba kembali pada "
                "jadwal berikutnya."
            )

            # Jangan crash/keluar
            time.sleep(3)

    # ========================================================
    # FINAL CLOSE
    # ========================================================

    close_browser()

    print()
    print("================================")
    print("PROGRAM SELESAI")
    print("================================")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()