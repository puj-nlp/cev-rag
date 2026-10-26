/** Static description of the cev-rag pipeline shown on the landing page. */

export const REPO_URL = 'https://github.com/puj-nlp/cev-rag';
export const repoFileUrl = (path) => `${REPO_URL}/blob/main/${path}`;

export const STAGES = ['ingest', 'chunk', 'embed', 'store', 'query', 'retrieve', 'generate'];
export const QUERY_STAGE_INDEX = STAGES.indexOf('query');
export const STAGE_DURATION = 3.5; // seconds per stage

export const COLORS = {
  background: '#0b1437',
  navy: '#1e3a8a',
  gold: '#fcd116',
  ochre: '#917d26',
  slate: '#94a3b8',
  sky: '#60a5fa',
  white: '#f8fafc',
};

export const NODES = {
  documents: {
    position: [-7, 0, 0],
    color: COLORS.sky,
    stages: ['ingest', 'chunk'],
    files: ['rag-api/scripts/build_milvus_db.py', 'notebook/simple_rag_v1.ipynb'],
  },
  embedding: {
    position: [-2.5, 0, 0],
    color: COLORS.gold,
    stages: ['embed'],
    files: ['rag-api/src/adapters/external/openai_services.py', 'rag-api/src/infrastructure/dimension_discovery.py'],
  },
  vectorStore: {
    position: [2, 0, 0],
    color: COLORS.sky,
    stages: ['store', 'retrieve'],
    files: ['rag-api/src/adapters/repositories/milvus_vector_db.py', 'docker-compose.yml'],
  },
  query: {
    position: [-2.5, 3.2, 0],
    color: COLORS.white,
    stages: ['query'],
    files: ['rag-ui/src/pages/UnifiedChatInterface.js', 'rag-api/src/adapters/controllers/frontend_controller.py'],
  },
  llm: {
    position: [6.5, 0, 0],
    color: COLORS.gold,
    stages: ['generate'],
    files: ['rag-api/src/adapters/external/openai_tools.py', 'rag-api/src/application/use_cases.py'],
  },
};

export const NODE_IDS = Object.keys(NODES);

/** Node emphasized during a stage. */
export const nodeForStage = (stage) => NODE_IDS.find((id) => NODES[id].stages.includes(stage));
