Melhorias


SELECT p.nome, m.nome, e.quantidade_atual from estoque as e 
JOIN medicamento as m on m.id_medicamento = e.id_medicamento
JOIN paciente as p on p.id_paciente = e.id_paciente WHERE m.id_medicamento = ?;

***Erro na função cadastrar_paciente_com_medicamentos():

SELECT p.nome AS paciente, 
               m.nome AS medicamento,  
               e.quantidade_atual as estoque
        FROM paciente p
        JOIN estoque e ON p.id_paciente = e.id_paciente
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento 
        WHERE p.stts = 1;
		
SELECT p.nome AS paciente
FROM paciente p
LEFT JOIN estoque e ON p.id_paciente = e.id_paciente
WHERE e.id_paciente IS NULL;
  
