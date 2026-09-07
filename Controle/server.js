const express = require('express');
const path = require('path');
const Calculadora = require('../Dominio/Calculadora/calculadora');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, '../Apresentacao')));
app.post('/calcular', (req, res) => {
    const { num1, num2, operacao } = req.body; 
    
    const calc = new Calculadora(); 
    let resultado;

    try {
        switch(operacao) {
            case 'somar': resultado = calc.somar(num1, num2); break;
            case 'subtrair': resultado = calc.subtrair(num1, num2); break;
            case 'multiplicar': resultado = calc.multiplicar(num1, num2); break;
            case 'dividir': resultado = calc.dividir(num1, num2); break;
            default: return res.status(400).json({ erro: "Operação inválida" });
        }
        res.json({ resultado: resultado }); 
    } catch (erro) {
        res.status(400).json({ erro: erro.message });
    }
});

app.listen(3000, () => {
    console.log('Servidor rodando! Abra http://localhost:3000 no seu navegador.');
});