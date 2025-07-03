from machine import ADC, PWM, Pin, UART, SoftI2C, I2C
from ssd1306 import SSD1306_I2C
from ads1x15 import ADS1115
import utime

# ----- MPU6050 -----
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')

    def read_raw(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        value = int.from_bytes(data, 'big')
        return value - 65536 if value >= 0x8000 else value

    def get_gyro(self):
        return [self.read_raw(r) / 131 for r in (0x43, 0x45, 0x47)]


# ----- Inicializações -----
servo = PWM(Pin(4))
servo.freq(50)

uart = UART(1, tx=Pin(8), rx=Pin(9), baudrate=9600)

i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

botao = Pin(5, Pin.IN, Pin.PULL_UP)
joy_x = ADC(1)

# ADS1115 com LDRs em A0 e A1
i2c_ads = I2C(1, scl=Pin(19), sda=Pin(18))
ads = ADS1115(i2c_ads, gain=1)

# MPU6050
i2c_mpu = I2C(0, scl=Pin(17), sda=Pin(16))
mpu = MPU6050(i2c_mpu)


# ----- Funções -----
def set_angle(angle):
    angle = max(0, min(180, angle))
    duty = int((angle / 180) * 8000 + 1000)
    servo.duty_u16(duty)

def mostrar_oled(modo, ldr_esq=None, ldr_dir=None, angulo=None):
    oled.fill(0)
    oled.text("Modo:", 0, 0)
    oled.text(modo, 50, 0)
    if ldr_esq is not None:
        oled.text(f"E: {int(ldr_esq)}", 0, 16)
    if ldr_dir is not None:
        oled.text(f"D: {int(ldr_dir)}", 70, 16)
    if angulo is not None:
        oled.text(f"Ang: {int(angulo)}", 0, 32)
    oled.show()


# ----- Variáveis iniciais -----
angulo = 90
set_angle(angulo)
utime.sleep(0.5)

modo_auto = True
parado = False
ultimo_estado_botao = 1
debounce_delay = 0.3

# Constantes PID
Kp = 150
Ki = 0.1
Kd = 20

# Estados do PID manual
erro_anterior = 0
integral_erro = 0

# Pesos dos LDRs
peso_esq = 1.0
peso_dir = 1.0

# ----- Loop principal -----
while True:
    # 🌀 Verifica movimento
    gyro = mpu.get_gyro()
    movimento_leve = any(abs(g) > 200 for g in gyro)

    if movimento_leve and not parado:
        parado = True
        uart.write("[ALERTA] Movimento detectado\n")
        mostrar_oled("PARADO")
        utime.sleep(0.5)

    if parado:
        mostrar_oled("PARADO")
        if botao.value() == 0:
            while botao.value() == 0:
                utime.sleep(0.1)
            parado = False
            uart.write("[INFO] Sistema retomado\n")
            mostrar_oled("RETOMANDO")
            utime.sleep(1)
        else:
            utime.sleep(0.2)
            continue

    # 🔁 Alternância de modo
    estado_botao = botao.value()
    if ultimo_estado_botao == 1 and estado_botao == 0:
        modo_auto = not modo_auto
        uart.write(f"[MODO] {'AUTO' if modo_auto else 'MANUAL'}\n")
        utime.sleep(debounce_delay)
    ultimo_estado_botao = estado_botao

    # 📥 Leitura dos LDRs
    ldr_esq = ads.read(channel1=2)
    ldr_dir = ads.read(channel1=3)

    if modo_auto:
        soma = ldr_esq + ldr_dir
        # 📐 Novo controle direto com base na diferença de luminosidade
        if soma == 0:
            erro_normalizado = 0
        else:
            erro_normalizado = (peso_esq * ldr_esq - peso_dir * ldr_dir) / soma

        # PID
        P = Kp * erro_normalizado
        integral_erro += erro_normalizado
        I = Ki * integral_erro
        derivada = erro_normalizado - erro_anterior
        D = Kd * derivada

        saida_pid = P + I + D
        erro_anterior = erro_normalizado

        angulo = max(0, min(180, 90 + saida_pid))
        set_angle(angulo)

        # Debug
        print("----- PID MANUAL -----")
        print(f"Erro norm : {erro_normalizado:.4f}")
        print(f"P         : {P:.4f}")
        print(f"I         : {I:.4f}")
        print(f"D         : {D:.4f}")
        print(f"Ângulo    : {angulo:.2f}")
        print("----------------------\n")
        uart.write(f"[AUTO] Esq: {ldr_esq} | Dir: {ldr_dir} | Ang: {int(angulo)}\n")
        mostrar_oled("AUTO", ldr_esq, ldr_dir, angulo)

    else:
        # 🕹 Controle manual com joystick
        leitura = joy_x.read_u16()
        if leitura < 30000:
            angulo = min(180, angulo + 2)
        elif leitura > 40000:
            angulo = max(0, angulo - 2)

        set_angle(angulo)
        uart.write(f"[MANUAL] Esq: {ldr_esq} | Dir: {ldr_dir} | Ang: {int(angulo)}\n")
        mostrar_oled("MANUAL", ldr_esq, ldr_dir, angulo)

    utime.sleep(0.3)


