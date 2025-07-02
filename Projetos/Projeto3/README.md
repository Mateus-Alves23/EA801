
# ☀️ Painéis Solares de Inclinação Adaptável V2.0 - BitDogLab

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

*(Inserir imagem do diagrama funcional aqui)*

## 🧠 Funcionamento do Código

O código implementa um sistema embarcado de rastreamento solar com dois modos de operação: automático com controle PID e manual com joystick. A seleção entre os modos é feita por um botão físico com debounce, enquanto a segurança do sistema é garantida por um sensor inercial (MPU6050) que pausa o sistema caso detecte movimento brusco (queda ou impacto).

Todos os dados operacionais — como modo ativo, ângulo atual e intensidade luminosa — são exibidos em tempo real no display OLED e enviados via Bluetooth por UART. O sistema utiliza sensores LDR conectados ao ADS1115 via I2C, joystick analógico via ADC, e atua sobre um servo motor SG90 controlado por PWM. O código foi escrito em MicroPython.

### 🔄 Máquina de Estados (MEF)


```python
erro_normalizado = (peso_esq * ldr_esq - peso_dir * ldr_dir) / soma
P = Kp * erro_normalizado
I = Ki * integral_erro
D = Kd * derivada
saida_pid = P + I + D
angulo = max(0, min(180, 90 + saida_pid))
```

### Modo Manual
```python
leitura = joy_x.read_u16()
if leitura < 30000:
    angulo += 2
elif leitura > 40000:
    angulo -= 2
```

### Segurança com MPU6050
```python
gyro = mpu.get_gyro()
movimento_leve = any(abs(g) > 200 for g in gyro)
```

### Alternância de Modos
```python
if ultimo_estado_botao == 1 and estado_botao == 0:
    modo_auto = not modo_auto
```

### Exibição no OLED e UART
```python
oled.text(f"Ang: {int(angulo)}", 0, 32)
uart.write(f"[AUTO] Esq: {ldr_esq} | Dir: {ldr_dir} | Ang: {int(angulo)}\n")
```

## Resultados Esperados

- Sistema funcional com resposta estável;
- Interface amigável e segura;
- Montagem robusta em PCB e estrutura 3D;
- Comunicação eficiente com o usuário.

## Equipe

- **Mateus Alves Silva** - RA: 239856  
- **Nathália Kaori Gondo** - RA: 239903  

---

Campinas, SP - 2024
