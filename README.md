# Funcionalidades Extra - Kanban Board

## Sistema de Prioridades

O sistema de prioridades foi implementado como uma funcionalidade essencial para melhorar a gestão e organização das tarefas no nosso Kanban Board. Esta funcionalidade permite aos utilizadores classificar as tarefas em três níveis de prioridade: Alta, Média e Baixa, cada uma representada por uma cor distinta na borda do cartão.

### Importância e Motivação

A implementação do sistema de prioridades surgiu da necessidade de:
- Permitir uma identificação visual rápida das tarefas mais urgentes
- Facilitar a tomada de decisão sobre qual tarefa abordar primeiro
- Melhorar a gestão do tempo e recursos da equipa
- Aumentar a eficiência no fluxo de trabalho

A distinção visual através de cores (vermelho para Alta, laranja para Média e verde para Baixa) permite uma compreensão imediata do nível de urgência de cada tarefa, mesmo sem necessidade de abrir o cartão para mais detalhes.

### Instruções de Utilização

1. Ao criar um novo cartão, a prioridade padrão é definida como "Baixa"
2. Para alterar a prioridade:
   - Localize o dropdown "Prioridade" no cartão
   - Selecione entre as opções: Alta, Média ou Baixa
   - A borda do cartão mudará automaticamente de cor para refletir a nova prioridade

## Sistema de Deadlines

O sistema de deadlines foi desenvolvido para complementar o sistema de prioridades, oferecendo uma gestão temporal mais precisa das tarefas. Esta funcionalidade permite definir datas limite para cada tarefa e fornece feedback visual baseado na proximidade do prazo.

### Importância e Motivação

A implementação do sistema de deadlines foi motivada por:
- Necessidade de controlo temporal das tarefas
- Prevenção de atrasos em projetos
- Melhor planeamento e distribuição do trabalho
- Facilitar a identificação de tarefas próximas do prazo

O sistema utiliza um esquema de cores de fundo para indicar o status temporal da tarefa:
- Vermelho claro: Prazo expirado
- Amarelo claro: Próximo do prazo (≤ 2 dias)
- Verde claro: Aproximando-se do prazo (≤ 5 dias)
- Branco: Prazo confortável (> 5 dias)

### Instruções de Utilização

1. Para definir um deadline:
   - Localize o campo "Deadline" no cartão
   - Insira a data no formato DD/MM/YYYY
   - O cartão mudará automaticamente de cor conforme a proximidade do prazo

2. Monitoramento:
   - Verifique a cor de fundo do cartão para uma rápida avaliação do status
   - Organize as tarefas baseando-se na combinação de prioridade e deadline

Estas funcionalidades trabalham em conjunto para proporcionar uma experiência mais completa e eficiente na gestão de tarefas, permitindo que as equipas mantenham um melhor controlo sobre seus projetos e prazos.