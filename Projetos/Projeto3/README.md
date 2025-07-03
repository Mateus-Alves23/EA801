
# Painéis Solares de Inclinação Adaptável V2.0 - BitDogLab

Projeto desenvolvido para a disciplina **EA801 - Laboratório de Projetos de Sistemas Embarcados** da **Faculdade de Engenharia Elétrica e de Computação (FEEC)** - **UNICAMP**.

## Descrição

A segunda versão do projeto *Painéis Solares de Inclinação Adaptável* visa o aprimoramento de um sistema embarcado inteligente utilizando a plataforma **BitDogLab** com **Raspberry Pi Pico** para simular o comportamento de painéis solares com inclinação variável.

O sistema opera em dois modos:

1. **Modo Automático (Sun Tracking)**: sensores LDR detectam a diferença de luminosidade e um controle PID ajusta dinamicamente o ângulo do painel.
2. **Modo Manual (Joystick)**: o usuário controla o painel diretamente usando um joystick analógico.

Inclui detecção de impactos via **MPU6050**, exibição de dados no **OLED** e transmissão via **Bluetooth HC-05**. A montagem foi feita em **PCB personalizada** e a estrutura mecânica foi desenvolvida em **CAD e impressa em 3D**.

## Objetivos

- Desenvolver um sistema robusto de rastreamento solar;
- Aplicar controle PID embarcado;
- Garantir segurança com MPU6050;
- Exibir dados no display OLED e transmitir por Bluetooth;
- Substituir protoboard por PCB e usar estrutura 3D impressa.

## Componentes Utilizados

- Raspberry Pi Pico com BitDogLab
- Sensores LDR
- Servo motor SG90
- Joystick analógico
- Display OLED SSD1306
- Botão A
- Bluetooth HC-05
- Sensor MPU6050
- Conversor analógico digital ADS1115
- PCB personalizada
- Estrutura mecânica impressa em 3D

## Diagrama de Blocos

![Diagrama de Blocos](Projetos/Projeto3/Fotos%20e%20V%C3%ADdeos/diagrama.png)

## Funcionamento do Código
[Código](https://github.com/Mateus-Alves23/EA801/blob/ebcd0ff22d0145f5401ba5697780aa0fe53728b3/Projetos/Projeto3/Adaptive_Solar_Panel_Tilt_System_V2.0.py)

O código implementa um sistema embarcado de rastreamento solar com dois modos de operação: automático com controle PID e manual com joystick. A seleção entre os modos é feita por um botão físico com debounce, enquanto a segurança do sistema é garantida por um sensor inercial (MPU6050) que pausa o sistema caso detecte movimento brusco (queda ou impacto).

Todos os dados operacionais — como modo ativo, ângulo atual e intensidade luminosa — são exibidos em tempo real no display OLED e enviados via Bluetooth por UART. O sistema utiliza sensores LDR conectados ao ADS1115 via I2C, joystick analógico via ADC, e atua sobre um servo motor SG90 controlado por PWM. O código foi escrito em MicroPython.

### Máquina de Estados (MEF)
O sistema opera com **três estados principais**:

1. **Estado “Parado” (SEGURANÇA)**  
   - Ativado quando o **MPU6050** detecta um movimento acima de 200°/s.
   - O sistema é interrompido (servo congelado, OLED mostra "PARADO").
   - Só volta ao estado anterior com a **pressão do botão físico**.

2. **Estado “Automático” (modo PID)**  
   - O sistema lê os LDRs e calcula o erro de luminosidade entre os lados.
   - O PID ajusta o ângulo do painel para buscar o ponto de maior intensidade luminosa.

3. **Estado “Manual” (modo Joystick)**  
   - O ângulo do painel é ajustado diretamente pelo joystick analógico.
   - Permite ao usuário explorar o sistema livremente.

**Transições:**
- `Parado → Operacional`: botão pressionado.
- `Operacional → Parado`: movimento detectado pelo MPU6050.
- `Automático ↔ Manual`: botão pressionado (com debounce).
---

### Loop Principal – Núcleo da execução

**Funções executadas a cada iteração:**
1. Leitura do giroscópio (MPU6050);
2. Verificação de segurança (modo "PARADO");
3. Troca de modo com debounce (botão físico);
4. Leitura dos LDRs (ADS1115);
5. Execução do PID ou leitura do joystick;
6. Atualização do servo motor;
7. Exibição no OLED e transmissão UART.

### Controle PID – Otimização da captação solar

```python
erro_normalizado = (peso_esq * ldr_esq - peso_dir * ldr_dir) / soma
P = Kp * erro_normalizado
I = Ki * integral_erro
D = Kd * (erro_normalizado - erro_anterior)
saida_pid = P + I + D
angulo = max(0, min(180, 90 + saida_pid))
```

Um **controlador PID** foi implementado para **ajustar o ângulo do painel solar** em tempo real com base na diferença de luminosidade entre os LDRs. O erro normalizado calcula o desbalanceamento entre os sensores e serve de entrada para o PID, que suavemente atualiza o ângulo do servo motor, evitando oscilações bruscas e mantendo o painel sempre apontado para a maior fonte de luz.

---

### Sensor Inercial MPU6050 – Segurança do sistema

```python
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

i2c_mpu = I2C(0, scl=Pin(17), sda=Pin(16))
mpu = MPU6050(i2c_mpu)

gyro = mpu.get_gyro()
movimento_leve = any(abs(g) > 200 for g in gyro)

    if movimento_leve and not parado:
        parado = True
        uart.write("[ALERTA] Movimento detectado\n")
        mostrar_oled("PARADO")
        utime.sleep(0.5)
```

O sensor **MPU6050** mede a rotação angular. Se qualquer eixo ultrapassar um limiar de segurança (200°/s), o sistema entra em **modo de pausa preventiva**. Esse mecanismo evita falhas ou acidentes em caso de quedas. A operação só é retomada com **intervenção do usuário** via botão físico.

---

### Leitura dos LDRs via ADS1115 – Sensoriamento de luz

```python
i2c_ads = I2C(1, scl=Pin(19), sda=Pin(18))
ads = ADS1115(i2c_ads, gain=1)

ldr_esq = ads.read(channel1=2)
ldr_dir = ads.read(channel1=3)
```

Os sensores LDR são conectados ao **ADS1115**, um conversor analógico-digital de alta precisão via **I2C**. As leituras dos canais A2 e A3 são usadas para calcular a distribuição de luz e orientar o painel. Essa abordagem garante maior estabilidade e precisão, comparada aos ADCs internos.

---

### Controle do servo motor – PWM e função `set_angle`

```python
servo = PWM(Pin(4))
servo.freq(50)

def set_angle(angle):
    angle = max(0, min(180, angle))
    duty = int((angle / 180) * 8000 + 1000)
    servo.duty_u16(duty)
```

O servo motor **SG90** é controlado via **PWM**, e a função `set_angle()` traduz o valor de ângulo (0–180°) para o pulso correspondente no duty cycle. Essa função é usada tanto pelo PID quanto pelo joystick.

---

### Display OLED – Interface local ao usuário

```python
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

oled.text("Modo:", 0, 0)
oled.text(modo, 50, 0)
oled.text(f"E: {int(ldr_esq)}", 0, 16)
oled.text(f"D: {int(ldr_dir)}", 70, 16)
oled.text(f"Ang: {int(angulo)}", 0, 32)
oled.show()
```

O display **OLED SSD1306**, via barramento I2C, fornece ao usuário uma interface visual amigável e informativa, exibindo o **modo de operação atual**, as **leituras dos LDRs** e o **ângulo do painel** em tempo real.

---

### Comunicação via UART (Bluetooth HC-05)
```python
uart = UART(1, tx=Pin(8), rx=Pin(9), baudrate=9600)

uart.write(f"[AUTO] Esq: {ldr_esq} | Dir: {ldr_dir} | Ang: {int(angulo)}\\n")
uart.write(f"[MANUAL] Esq: {ldr_esq} | Dir: {ldr_dir} | Ang: {int(angulo)}\\n")
uart.write("[ALERTA] Movimento detectado\\n")
uart.write("[INFO] Sistema retomado\\n")
```
A UART é utilizada para transmitir mensagens informativas ao celular via Bluetooth HC-05.
Ela indica o modo de operação atual, os valores dos sensores e o ângulo do painel. Também envia alertas de segurança e retomada do sistema.

## Resultados
[Fotos e Vídeos](https://github.com/Mateus-Alves23/EA801/tree/4adf623515919757887739d8a4f3288d6da433ca/Projetos/Projeto3/Fotos%20e%20V%C3%ADdeos)

[PCB](https://github.com/Mateus-Alves23/EA801/tree/ebcd0ff22d0145f5401ba5697780aa0fe53728b3/Projetos/Projeto3/PCB)

[Modelo 3D](https://github.com/Mateus-Alves23/EA801/tree/ebcd0ff22d0145f5401ba5697780aa0fe53728b3/Projetos/Projeto3/Modelo%203D)


O sistema desenvolvido mostrou-se **altamente responsivo**, com tempos de reação rápidos aos estímulos luminosos. O controle PID apresentou um leve **overshoot**, o que é esperado em sistemas dinâmicos, mas manteve **estabilidade geral** e bom acompanhamento da luz incidente.

Todos os subsistemas — controle PID, leitura dos LDRs via ADS1115, atuação do servo motor, exibição no OLED, comunicação via Bluetooth e segurança com o MPU6050 — **funcionaram corretamente em paralelo**, demonstrando **boa integração e robustez do projeto**.

O sistema de segurança, baseado no MPU6050, **agiu de forma satisfatória e rápida** diante de movimentações bruscas, pausando o sistema conforme esperado e garantindo proteção ao hardware.

### Dificuldades encontradas

- A principal dificuldade foi a **regulagem dos parâmetros do PID**, que exigiu múltiplas iterações por tentativa e erro para encontrar um ajuste que proporcionasse **resposta veloz** sem **overshoot exagerado**.
- A **soldagem da PCB** apresentou desafios devido a limitações na qualidade da impressão do layout, o que comprometeu temporariamente algumas conexões, **especialmente nas linhas de comunicação I²C**.
- Apesar dessas dificuldades, com **revisões e retrabalho cuidadoso**, o sistema foi restaurado à sua plena funcionalidade.

## Equipe

- **Mateus Alves Silva** - RA: 239856  
- **Nathália Kaori Gondo** - RA: 239903  

---

Campinas, SP - 2025
