# 🐍 Projeto Snake Game – BitDogLab

## 👥 Integrantes do Grupo

- **Mateus Alves Silva** – RA: 239856
- **Nathália Kaori Gondo** – RA: 239903

## 🔗 Documentação e Apresentação

- 📄 Relatório do projeto no Google Docs: [Clique aqui para acessar]([https://link-do-documento-no-gdocs](https://docs.google.com/document/d/1dpaKRoc5Zu-8dQmBL2AY7nqhb6fK013XJ1xV9JeQEso/edit?usp=sharing))  
- 📄 Proposta do projeto no Google Docs: [Clique aqui para acessar]([[https://link-do-documento-no-gdocs](https://docs.google.com/document/d/1dpaKRoc5Zu-8dQmBL2AY7nqhb6fK013XJ1xV9JeQEso/edit?usp=sharing](https://docs.google.com/document/d/1hUa7evTsGhv2qcS7_uBKVWjl4HW6heMswdRRUvuTeMQ/edit?usp=sharing)))
- 
> Se desejar, peça à BitDogLab para adicionar este link ao repositório oficial do projeto.

---

## 📌 Descrição Detalhada

Este projeto consiste na implementação de um **jogo da cobrinha (Snake Game)** utilizando **MicroPython** com a plataforma **Raspberry Pi Pico** e periféricos conectados via GPIO/I2C/PWM.  

O objetivo principal foi **criar uma versão jogável do clássico Snake**, utilizando os seguintes recursos de hardware:

- **Joystick analógico**: para controlar a direção da cobrinha  
- **Display OLED (128x64)**: para exibir pontuação e mensagens  
- **Matriz de LEDs WS2812 (5x5)**: para mostrar a cobrinha e a comida  
- **Buzzer PWM**: para efeitos sonoros durante o jogo (início, derrota, vitória)  
- **Botão A**: utilizado para iniciar a partida

O código foi desenvolvido com foco em legibilidade, modularidade e documentação, de forma que qualquer aluno ou pessoa interessada consiga entender e reproduzir o funcionamento do sistema.

---

## 💻 Software Comentado

O código está completamente comentado, com:

- Explicações **linha por linha** de cada instrução  
- Comentários de **bloco**, indicando a função de cada parte do programa  
- Comentários em **todas as funções**, explicando objetivos e funcionamento  

Todos os periféricos foram devidamente configurados em MicroPython, e o código foi organizado para permitir futuras expansões, como placar com armazenamento ou aumento do tamanho da matriz.

O jogo está estruturado da seguinte forma:

- Contagem regressiva na matriz de LEDs e no OLED antes de começar
- Controle da cobrinha via joystick analógico
- Comida aleatória sendo posicionada em locais não ocupados
- Sons diferentes para início, vitória e derrota
- Detecção de colisões com o próprio corpo
- Pontuação exibida em tempo real

---

## ✅ Resultados

- ✅ **Jogo funcional** com movimentação fluida da cobrinha e controle preciso via joystick  
- ✅ **Feedback sonoro completo** com efeitos para diferentes eventos do jogo  
- ✅ **Interface visual atrativa**, com uso simultâneo de matriz de LEDs e display OLED  
- ✅ **Código limpo, modular e bem documentado**, facilitando a leitura e entendimento por terceiros  
- ✅ **Comportamento cíclico nas bordas**, como no jogo clássico: a cobrinha atravessa e reaparece do outro lado  
- ✅ **Exibição de tela de vitória e derrota**, com sons e mensagens diferentes  
- ✅ Ideal para aprendizagem de integração entre múltiplos periféricos com MicroPython

---
