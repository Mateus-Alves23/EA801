
## 🧠 Funcionamento Geral do Código

O código implementa um sistema embarcado de rastreamento solar com dois modos de operação: **automático com controle PID** e **manual com joystick**. A seleção entre os modos é feita por um botão físico com debounce, enquanto a segurança do sistema é garantida por um sensor inercial (**MPU6050**) que pausa o sistema caso detecte movimento brusco (queda ou impacto).

Todos os dados operacionais — como modo ativo, ângulo atual e intensidade luminosa — são exibidos em tempo real no **display OLED** e enviados via **Bluetooth** por UART. O sistema utiliza sensores LDR conectados ao **ADS1115 via I2C**, joystick analógico via ADC, e atua sobre um **servo motor SG90 controlado por PWM**.

---

## 🔄 Máquina de Estados (MEF)

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

## 🔧 Seções Detalhadas do Código

### ⚙️ Controle PID – Otimização da captação solar

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

### 🛑 Sensor Inercial MPU6050 – Segurança do sistema

```python
gyro = mpu.get_gyro()
movimento_leve = any(abs(g) > 200 for g in gyro)
```

O sensor **MPU6050** mede a rotação angular. Se qualquer eixo ultrapassar um limiar de segurança (200°/s), o sistema entra em **modo de pausa preventiva**. Esse mecanismo evita falhas ou acidentes em caso de quedas. A operação só é retomada com **intervenção do usuário** via botão físico.

---

### 🌞 Leitura dos LDRs via ADS1115 – Sensoriamento de luz

```python
ldr_esq = ads.read(channel1=2)
ldr_dir = ads.read(channel1=3)
```

Os sensores LDR são conectados ao **ADS1115**, um conversor analógico-digital de alta precisão via **I2C**. As leituras dos canais A2 e A3 são usadas para calcular a distribuição de luz e orientar o painel. Essa abordagem garante maior estabilidade e precisão, comparada aos ADCs internos.

---

### 🎯 Controle do servo motor – PWM e função `set_angle`

```python
def set_angle(angle):
    angle = max(0, min(180, angle))
    duty = int((angle / 180) * 8000 + 1000)
    servo.duty_u16(duty)
```

O servo motor **SG90** é controlado via **PWM**, e a função `set_angle()` traduz o valor de ângulo (0–180°) para o pulso correspondente no duty cycle. Essa função é usada tanto pelo PID quanto pelo joystick.

---

### 🖥️ Display OLED – Interface local ao usuário

```python
oled.text("Modo:", 0, 0)
oled.text(modo, 50, 0)
oled.text(f"E: {int(ldr_esq)}", 0, 16)
oled.text(f"D: {int(ldr_dir)}", 70, 16)
oled.text(f"Ang: {int(angulo)}", 0, 32)
oled.show()
```

O display **OLED SSD1306**, via barramento I2C, fornece ao usuário uma interface visual amigável e informativa, exibindo o **modo de operação atual**, as **leituras dos LDRs** e o **ângulo do painel** em tempo real.

---

### 🔁 Loop Principal – Núcleo da execução

**Funções executadas a cada iteração:**
1. Leitura do giroscópio (MPU6050);
2. Verificação de segurança (modo "PARADO");
3. Troca de modo com debounce (botão físico);
4. Leitura dos LDRs (ADS1115);
5. Execução do PID ou leitura do joystick;
6. Atualização do servo motor;
7. Exibição no OLED e transmissão UART.

**Exemplo de alternância entre modos:**
```python
if ultimo_estado_botao == 1 and estado_botao == 0:
    modo_auto = not modo_auto
    uart.write(f"[MODO] {'AUTO' if modo_auto else 'MANUAL'}\n")
```
