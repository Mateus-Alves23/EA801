
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
- PCB personalizada
- Estrutura mecânica impressa em 3D

## Diagrama de Blocos

*(Inserir imagem do diagrama funcional aqui)*

## Software Comentado

O código foi escrito em MicroPython. Destaques:

### Controle PID
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
