# Matriz de atendimento aos requisitos

| Requisito da atividade | Implementação | Verificação |
| --- | --- | --- |
| Criar, listar e remover usuários | `GerenciadorTarefas` e `Usuario` | `test_cadastro_listagem_e_remocao_de_usuario` |
| Criar, listar e remover projetos por usuário | `Usuario.criar_projeto`, `listar_projetos` e `remover_projeto` | `test_usuario_cria_lista_e_remove_projetos` |
| Várias tarefas por projeto | `Projeto._tarefas` e operações de tarefa | `test_tarefas_status_atraso_e_progresso_do_projeto` |
| Título, descrição, prioridade, prazo e status | Classe `Tarefa` e enums | Testes de tarefa e validação |
| Quatro níveis de prioridade | Enum `Prioridade` | Testes de relatórios e exportação |
| Pendente, em andamento e concluída | Enum `StatusTarefa` | Teste de ciclo de status |
| Percentual concluído por projeto | `Projeto.calcular_progresso` | Testes de progresso e relatórios |
| Pendências por prioridade | `tarefas_pendentes_por_prioridade` | `test_relatorios_de_produtividade` |
| Projetos com maior conclusão | `projetos_por_progresso` | `test_relatorios_de_produtividade` |
| Concluídas por usuário | `total_concluidas_por_usuario` | `test_relatorios_de_produtividade` |
| Exportação opcional TXT/CSV | `ExportadorCSV` e `ExportadorTXT` | Teste CSV e demonstração TXT |
| Repositório organizado e documentado | Estrutura `src`, `tests`, `docs` e `README.md` | Revisão de estrutura e histórico Git |

