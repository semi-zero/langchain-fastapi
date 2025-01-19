private async createAnsweringChainExternal(
    llm: BaseChatModel,
    fileIds: string[],
    embeddings: Embeddings,
    optimizationMode: 'speed' | 'balanced' | 'quality',
  ) {
    console.log('[createAnsweringChainExternal] Creating chain with mode:', optimizationMode);
    console.log('[createAnsweringChainExternal] File IDs:', fileIds);
  
    return RunnableSequence.from([
      RunnableMap.from({
        query: (input: BasicChainInput) => input.query,
        chat_history: (input: BasicChainInput) => input.chat_history,
        date: () => new Date().toISOString(),
        context: RunnableLambda.from(async (input: BasicChainInput) => {
          try {
            const response = await fetch('http://your-fastapi-url/process', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                query: input.query,
                chat_history: formatChatHistoryAsString(input.chat_history),
                file_ids: fileIds,
                optimization_mode: optimizationMode,
                search_web: this.config.searchWeb,
                rerank_threshold: this.config.rerankThreshold
              }),
            });
  
            if (!response.ok) {
              throw new Error('FastAPI 서버 응답 오류');
            }
  
            const data = await response.json();
            return this.processDocs(data.documents);
          } catch (error) {
            console.error('[createAnsweringChainExternal] Error:', error);
            throw error;
          }
        }).withConfig({
          runName: 'FinalSourceRetriever',
        }),
      }),
      ChatPromptTemplate.fromMessages([
        ['system', this.config.responsePrompt],
        new MessagesPlaceholder('chat_history'),
        ['user', '{query}'],
      ]),
      llm,
      this.strParser,
    ]).withConfig({
      runName: 'FinalResponseGenerator',
    });
  }