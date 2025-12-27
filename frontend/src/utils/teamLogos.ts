/**
 * Mapeamento de logos locais de times
 *
 * Este utilitário permite buscar logos de times armazenadas localmente
 * em /public/logos/ sem necessidade de chamadas à API externa.
 */

/**
 * Mapa de slug do time → caminho da logo
 * Gerado a partir dos arquivos em /public/logos/
 */
const LOGO_PATHS: Record<string, string> = {
  // England - Premier League
  'arsenal': '/logos/england/premier-league/arsenal.png',
  'aston-villa': '/logos/england/premier-league/aston-villa.png',
  'bournemouth': '/logos/england/premier-league/bournemouth.png',
  'afc-bournemouth': '/logos/england/premier-league/bournemouth.png',
  'brentford': '/logos/england/premier-league/brentford.png',
  'brighton-and-hove-albion': '/logos/england/premier-league/brighton-and-hove-albion.png',
  'brighton-hove-albion': '/logos/england/premier-league/brighton-and-hove-albion.png',
  'brighton': '/logos/england/premier-league/brighton-and-hove-albion.png',
  'burnley': '/logos/england/premier-league/burnley.png',
  'chelsea': '/logos/england/premier-league/chelsea.png',
  'crystal-palace': '/logos/england/premier-league/crystal-palace.png',
  'everton': '/logos/england/premier-league/everton.png',
  'fulham': '/logos/england/premier-league/fulham.png',
  'leeds-united': '/logos/england/premier-league/leeds-united.png',
  'liverpool': '/logos/england/premier-league/liverpool.png',
  'manchester-city': '/logos/england/premier-league/manchester-city.png',
  'manchester-united': '/logos/england/premier-league/manchester-united.png',
  'newcastle-united': '/logos/england/premier-league/newcastle-united.png',
  'newcastle': '/logos/england/premier-league/newcastle-united.png',
  'nottingham-forest': '/logos/england/premier-league/nottingham-forest.png',
  'sunderland': '/logos/england/premier-league/sunderland.png',
  'tottenham-hotspur': '/logos/england/premier-league/tottenham-hotspur.png',
  'tottenham': '/logos/england/premier-league/tottenham-hotspur.png',
  'west-ham-united': '/logos/england/premier-league/west-ham-united.png',
  'west-ham': '/logos/england/premier-league/west-ham-united.png',
  'wolverhampton-wanderers': '/logos/england/premier-league/wolverhampton-wanderers.png',
  'wolverhampton': '/logos/england/premier-league/wolverhampton-wanderers.png',
  'wolves': '/logos/england/premier-league/wolverhampton-wanderers.png',

  // England - Championship
  'birmingham-city': '/logos/england/championship/birmingham-city.png',
  'blackburn-rovers': '/logos/england/championship/blackburn-rovers.png',
  'bristol-city': '/logos/england/championship/bristol-city.png',
  'charlton-athletic': '/logos/england/championship/charlton-athletic.png',
  'coventry-city': '/logos/england/championship/coventry-city.png',
  'derby-county': '/logos/england/championship/derby-county.png',
  'hull-city': '/logos/england/championship/hull-city.png',
  'ipswich-town': '/logos/england/championship/ipswich-town.png',
  'leicester-city': '/logos/england/championship/leicester-city.png',
  'middlesbrough': '/logos/england/championship/middlesbrough.png',
  'millwall': '/logos/england/championship/millwall.png',
  'norwich-city': '/logos/england/championship/norwich-city.png',
  'oxford-united': '/logos/england/championship/oxford-united.png',
  'portsmouth': '/logos/england/championship/portsmouth.png',
  'preston-north-end': '/logos/england/championship/preston-north-end.png',
  'queens-park-rangers': '/logos/england/championship/queens-park-rangers.png',
  'qpr': '/logos/england/championship/queens-park-rangers.png',
  'sheffield-united': '/logos/england/championship/sheffield-united.png',
  'sheffield-wednesday': '/logos/england/championship/sheffield-wednesday.png',
  'southampton': '/logos/england/championship/southampton.png',
  'stoke-city': '/logos/england/championship/stoke-city.png',
  'swansea-city': '/logos/england/championship/swansea-city.png',
  'watford': '/logos/england/championship/watford.png',
  'west-bromwich-albion': '/logos/england/championship/west-bromwich-albion.png',
  'west-brom': '/logos/england/championship/west-bromwich-albion.png',
  'wrexham': '/logos/england/championship/wrexham.png',

  // Italy - Serie A
  'ac-milan': '/logos/italy/serie-a/ac-milan.png',
  'milan': '/logos/italy/serie-a/ac-milan.png',
  'atalanta': '/logos/italy/serie-a/atalanta.png',
  'bologna': '/logos/italy/serie-a/bologna.png',
  'cagliari': '/logos/italy/serie-a/cagliari.png',
  'como': '/logos/italy/serie-a/como.png',
  'cremonese': '/logos/italy/serie-a/cremonese.png',
  'fiorentina': '/logos/italy/serie-a/fiorentina.png',
  'genoa': '/logos/italy/serie-a/genoa.png',
  'hellas-verona': '/logos/italy/serie-a/hellas-verona.png',
  'verona': '/logos/italy/serie-a/hellas-verona.png',
  'inter-milan': '/logos/italy/serie-a/inter-milan.png',
  'inter': '/logos/italy/serie-a/inter-milan.png',
  'internazionale': '/logos/italy/serie-a/inter-milan.png',
  'juventus': '/logos/italy/serie-a/juventus.png',
  'lazio': '/logos/italy/serie-a/lazio.png',
  'lecce': '/logos/italy/serie-a/lecce.png',
  'napoli': '/logos/italy/serie-a/napoli.png',
  'parma': '/logos/italy/serie-a/parma.png',
  'pisa': '/logos/italy/serie-a/pisa.png',
  'roma': '/logos/italy/serie-a/roma.png',
  'as-roma': '/logos/italy/serie-a/roma.png',
  'sassuolo': '/logos/italy/serie-a/sassuolo.png',
  'torino': '/logos/italy/serie-a/torino.png',
  'udinese': '/logos/italy/serie-a/udinese.png',

  // Italy - Serie B
  'avellino': '/logos/italy/serie-b/avellino.png',
  'bari': '/logos/italy/serie-b/bari.png',
  'carrarese': '/logos/italy/serie-b/carrarese.png',
  'catanzaro': '/logos/italy/serie-b/catanzaro.png',
  'cesena': '/logos/italy/serie-b/cesena.png',
  'empoli': '/logos/italy/serie-b/empoli.png',
  'frosinone': '/logos/italy/serie-b/frosinone.png',
  'juve-stabia': '/logos/italy/serie-b/juve-stabia.png',
  'mantova': '/logos/italy/serie-b/mantova.png',
  'modena': '/logos/italy/serie-b/modena.png',
  'monza': '/logos/italy/serie-b/monza.png',
  'padova': '/logos/italy/serie-b/padova.png',
  'palermo': '/logos/italy/serie-b/palermo.png',
  'pescara': '/logos/italy/serie-b/pescara.png',
  'reggiana': '/logos/italy/serie-b/reggiana.png',
  'sampdoria': '/logos/italy/serie-b/sampdoria.png',
  'spezia': '/logos/italy/serie-b/spezia.png',
  'sudtirol': '/logos/italy/serie-b/sudtirol.png',
  'venezia': '/logos/italy/serie-b/venezia.png',
  'virtus-entella': '/logos/italy/serie-b/virtus-entella.png',

  // Spain - La Liga
  'athletic-bilbao': '/logos/spain/la-liga/athletic-bilbao.png',
  'athletic-club': '/logos/spain/la-liga/athletic-bilbao.png',
  'atletico-madrid': '/logos/spain/la-liga/atletico-madrid.png',
  'atletico-de-madrid': '/logos/spain/la-liga/atletico-madrid.png',
  'barcelona': '/logos/spain/la-liga/barcelona.png',
  'fc-barcelona': '/logos/spain/la-liga/barcelona.png',
  'celta-vigo': '/logos/spain/la-liga/celta-vigo.png',
  'celta-de-vigo': '/logos/spain/la-liga/celta-vigo.png',
  'deportivo-alaves': '/logos/spain/la-liga/deportivo-alaves.png',
  'alaves': '/logos/spain/la-liga/deportivo-alaves.png',
  'elche': '/logos/spain/la-liga/elche.png',
  'espanyol': '/logos/spain/la-liga/espanyol.png',
  'getafe': '/logos/spain/la-liga/getafe.png',
  'girona': '/logos/spain/la-liga/girona.png',
  'levante': '/logos/spain/la-liga/levante.png',
  'mallorca': '/logos/spain/la-liga/mallorca.png',
  'osasuna': '/logos/spain/la-liga/osasuna.png',
  'rayo-vallecano': '/logos/spain/la-liga/rayo-vallecano.png',
  'real-betis': '/logos/spain/la-liga/real-betis.png',
  'betis': '/logos/spain/la-liga/real-betis.png',
  'real-madrid': '/logos/spain/la-liga/real-madrid.png',
  'real-oviedo': '/logos/spain/la-liga/real-oviedo.png',
  'real-sociedad': '/logos/spain/la-liga/real-sociedad.png',
  'sevilla': '/logos/spain/la-liga/sevilla.png',
  'valencia': '/logos/spain/la-liga/valencia.png',
  'villarreal': '/logos/spain/la-liga/villarreal.png',

  // Spain - La Liga 2
  'albacete': '/logos/spain/la-liga-2/albacete.png',
  'almeria': '/logos/spain/la-liga-2/almeria.png',
  'burgos': '/logos/spain/la-liga-2/burgos.png',
  'cadiz': '/logos/spain/la-liga-2/cadiz.png',
  'castellon': '/logos/spain/la-liga-2/castellon.png',
  'ceuta': '/logos/spain/la-liga-2/ceuta.png',
  'cordoba': '/logos/spain/la-liga-2/cordoba.png',
  'cultural-leonesa': '/logos/spain/la-liga-2/cultural-leonesa.png',
  'deportivo-de-la-coruna': '/logos/spain/la-liga-2/deportivo-de-la-coruna.png',
  'deportivo': '/logos/spain/la-liga-2/deportivo-de-la-coruna.png',
  'eibar': '/logos/spain/la-liga-2/eibar.png',
  'fc-andorra': '/logos/spain/la-liga-2/fc-andorra.png',
  'granada': '/logos/spain/la-liga-2/granada.png',
  'huesca': '/logos/spain/la-liga-2/huesca.png',
  'las-palmas': '/logos/spain/la-liga-2/las-palmas.png',
  'leganes': '/logos/spain/la-liga-2/leganes.png',
  'malaga': '/logos/spain/la-liga-2/malaga.png',
  'mirandes': '/logos/spain/la-liga-2/mirandes.png',
  'racing-de-santander': '/logos/spain/la-liga-2/racing-de-santander.png',
  'racing-santander': '/logos/spain/la-liga-2/racing-de-santander.png',
  'real-sociedad-b': '/logos/spain/la-liga-2/real-sociedad-b.png',
  'real-valladolid': '/logos/spain/la-liga-2/real-valladolid.png',
  'valladolid': '/logos/spain/la-liga-2/real-valladolid.png',
  'real-zaragoza': '/logos/spain/la-liga-2/real-zaragoza.png',
  'zaragoza': '/logos/spain/la-liga-2/real-zaragoza.png',
  'sporting-de-gijon': '/logos/spain/la-liga-2/sporting-de-gijon.png',
  'sporting-gijon': '/logos/spain/la-liga-2/sporting-de-gijon.png',

  // Germany - Bundesliga
  'bayer-leverkusen': '/logos/germany/bundesliga/bayer-leverkusen.png',
  'leverkusen': '/logos/germany/bundesliga/bayer-leverkusen.png',
  'bayern-munich': '/logos/germany/bundesliga/bayern-munich.png',
  'bayern-munchen': '/logos/germany/bundesliga/bayern-munich.png',
  'bayern': '/logos/germany/bundesliga/bayern-munich.png',
  'borussia-dortmund': '/logos/germany/bundesliga/borussia-dortmund.png',
  'dortmund': '/logos/germany/bundesliga/borussia-dortmund.png',
  'borussia-monchengladbach': '/logos/germany/bundesliga/borussia-monchengladbach.png',
  'monchengladbach': '/logos/germany/bundesliga/borussia-monchengladbach.png',
  'gladbach': '/logos/germany/bundesliga/borussia-monchengladbach.png',
  'eintracht-frankfurt': '/logos/germany/bundesliga/eintracht-frankfurt.png',
  'frankfurt': '/logos/germany/bundesliga/eintracht-frankfurt.png',
  'fc-augsburg': '/logos/germany/bundesliga/fc-augsburg.png',
  'augsburg': '/logos/germany/bundesliga/fc-augsburg.png',
  'fc-heidenheim': '/logos/germany/bundesliga/fc-heidenheim.png',
  'heidenheim': '/logos/germany/bundesliga/fc-heidenheim.png',
  'fc-koln': '/logos/germany/bundesliga/fc-koln.png',
  'koln': '/logos/germany/bundesliga/fc-koln.png',
  'cologne': '/logos/germany/bundesliga/fc-koln.png',
  'freiburg': '/logos/germany/bundesliga/freiburg.png',
  'hamburg': '/logos/germany/bundesliga/hamburg.png',
  'hamburger-sv': '/logos/germany/bundesliga/hamburg.png',
  'hoffenheim': '/logos/germany/bundesliga/hoffenheim.png',
  'tsg-hoffenheim': '/logos/germany/bundesliga/hoffenheim.png',
  'mainz': '/logos/germany/bundesliga/mainz.png',
  'mainz-05': '/logos/germany/bundesliga/mainz.png',
  'rb-leipzig': '/logos/germany/bundesliga/rb-leipzig.png',
  'leipzig': '/logos/germany/bundesliga/rb-leipzig.png',
  'st-pauli': '/logos/germany/bundesliga/st-pauli.png',
  'stuttgart': '/logos/germany/bundesliga/stuttgart.png',
  'vfb-stuttgart': '/logos/germany/bundesliga/stuttgart.png',
  'union-berlin': '/logos/germany/bundesliga/union-berlin.png',
  'werder-bremen': '/logos/germany/bundesliga/werder-bremen.png',
  'bremen': '/logos/germany/bundesliga/werder-bremen.png',
  'wolfsburg': '/logos/germany/bundesliga/wolfsburg.png',

  // Germany - 2. Bundesliga
  'arminia-bielefeld': '/logos/germany/2-bundesliga/arminia-bielefeld.png',
  'bielefeld': '/logos/germany/2-bundesliga/arminia-bielefeld.png',
  'bochum': '/logos/germany/2-bundesliga/bochum.png',
  'darmstadt': '/logos/germany/2-bundesliga/darmstadt.png',
  'dynamo-dresden': '/logos/germany/2-bundesliga/dynamo-dresden.png',
  'dresden': '/logos/germany/2-bundesliga/dynamo-dresden.png',
  'eintracht-braunschweig': '/logos/germany/2-bundesliga/eintracht-braunschweig.png',
  'braunschweig': '/logos/germany/2-bundesliga/eintracht-braunschweig.png',
  'elversberg': '/logos/germany/2-bundesliga/elversberg.png',
  'fc-nurnberg': '/logos/germany/2-bundesliga/fc-nurnberg.png',
  'nurnberg': '/logos/germany/2-bundesliga/fc-nurnberg.png',
  'fortuna-dusseldorf': '/logos/germany/2-bundesliga/fortuna-dusseldorf.png',
  'dusseldorf': '/logos/germany/2-bundesliga/fortuna-dusseldorf.png',
  'greuther-furth': '/logos/germany/2-bundesliga/greuther-furth.png',
  'furth': '/logos/germany/2-bundesliga/greuther-furth.png',
  'hannover': '/logos/germany/2-bundesliga/hannover.png',
  'hannover-96': '/logos/germany/2-bundesliga/hannover.png',
  'hertha': '/logos/germany/2-bundesliga/hertha.png',
  'hertha-bsc': '/logos/germany/2-bundesliga/hertha.png',
  'holstein-kiel': '/logos/germany/2-bundesliga/holstein-kiel.png',
  'kiel': '/logos/germany/2-bundesliga/holstein-kiel.png',
  'kaiserslautern': '/logos/germany/2-bundesliga/kaiserslautern.png',
  'karlsruhe': '/logos/germany/2-bundesliga/karlsruhe.png',
  'karlsruher-sc': '/logos/germany/2-bundesliga/karlsruhe.png',
  'magdeburg': '/logos/germany/2-bundesliga/magdeburg.png',
  'paderborn': '/logos/germany/2-bundesliga/paderborn.png',
  'preuen-munster': '/logos/germany/2-bundesliga/preuen-munster.png',
  'schalke-04': '/logos/germany/2-bundesliga/schalke-04.png',
  'schalke': '/logos/germany/2-bundesliga/schalke-04.png',

  // France - Ligue 1
  'angers': '/logos/france/ligue-1/angers.png',
  'auxerre': '/logos/france/ligue-1/auxerre.png',
  'brest': '/logos/france/ligue-1/brest.png',
  'le-havre': '/logos/france/ligue-1/le-havre.png',
  'lens': '/logos/france/ligue-1/lens.png',
  'lille': '/logos/france/ligue-1/lille.png',
  'lorient': '/logos/france/ligue-1/lorient.png',
  'lyon': '/logos/france/ligue-1/lyon.png',
  'olympique-lyonnais': '/logos/france/ligue-1/lyon.png',
  'marseille': '/logos/france/ligue-1/marseille.png',
  'olympique-marseille': '/logos/france/ligue-1/marseille.png',
  'metz': '/logos/france/ligue-1/metz.png',
  'monaco': '/logos/france/ligue-1/monaco.png',
  'as-monaco': '/logos/france/ligue-1/monaco.png',
  'nantes': '/logos/france/ligue-1/nantes.png',
  'nice': '/logos/france/ligue-1/nice.png',
  'ogc-nice': '/logos/france/ligue-1/nice.png',
  'paris-fc': '/logos/france/ligue-1/paris-fc.png',
  'paris-sg': '/logos/france/ligue-1/paris-sg.png',
  'psg': '/logos/france/ligue-1/paris-sg.png',
  'paris-saint-germain': '/logos/france/ligue-1/paris-sg.png',
  'rennes': '/logos/france/ligue-1/rennes.png',
  'stade-rennais': '/logos/france/ligue-1/rennes.png',
  'strasbourg': '/logos/france/ligue-1/strasbourg.png',
  'toulouse': '/logos/france/ligue-1/toulouse.png',

  // France - Ligue 2
  'amiens': '/logos/france/ligue-2/amiens.png',
  'annecy': '/logos/france/ligue-2/annecy.png',
  'bastia': '/logos/france/ligue-2/bastia.png',
  'boulogne': '/logos/france/ligue-2/boulogne.png',
  'clermont-foot': '/logos/france/ligue-2/clermont-foot.png',
  'clermont': '/logos/france/ligue-2/clermont-foot.png',
  'grenoble': '/logos/france/ligue-2/grenoble.png',
  'guingamp': '/logos/france/ligue-2/guingamp.png',
  'laval': '/logos/france/ligue-2/laval.png',
  'le-mans': '/logos/france/ligue-2/le-mans.png',
  'montpellier': '/logos/france/ligue-2/montpellier.png',
  'nancy-lorraine': '/logos/france/ligue-2/nancy-lorraine.png',
  'nancy': '/logos/france/ligue-2/nancy-lorraine.png',
  'pau-fc': '/logos/france/ligue-2/pau-fc.png',
  'pau': '/logos/france/ligue-2/pau-fc.png',
  'red-star': '/logos/france/ligue-2/red-star.png',
  'rodez-af': '/logos/france/ligue-2/rodez-af.png',
  'rodez': '/logos/france/ligue-2/rodez-af.png',
  'stade-de-reims': '/logos/france/ligue-2/stade-de-reims.png',
  'reims': '/logos/france/ligue-2/stade-de-reims.png',
  'st-etienne': '/logos/france/ligue-2/st-etienne.png',
  'saint-etienne': '/logos/france/ligue-2/st-etienne.png',
  'troyes': '/logos/france/ligue-2/troyes.png',
  'usl-dunkerque': '/logos/france/ligue-2/usl-dunkerque.png',
  'dunkerque': '/logos/france/ligue-2/usl-dunkerque.png',

  // Portugal - Primeira Liga
  'alverca': '/logos/portugal/primeira-liga/alverca.png',
  'arouca': '/logos/portugal/primeira-liga/arouca.png',
  'avs': '/logos/portugal/primeira-liga/avs.png',
  'benfica': '/logos/portugal/primeira-liga/benfica.png',
  'sl-benfica': '/logos/portugal/primeira-liga/benfica.png',
  'braga': '/logos/portugal/primeira-liga/braga.png',
  'sc-braga': '/logos/portugal/primeira-liga/braga.png',
  'casa-pia': '/logos/portugal/primeira-liga/casa-pia.png',
  'estoril-praia': '/logos/portugal/primeira-liga/estoril-praia.png',
  'estoril': '/logos/portugal/primeira-liga/estoril-praia.png',
  'estrela-amadora': '/logos/portugal/primeira-liga/estrela-amadora.png',
  'estrela': '/logos/portugal/primeira-liga/estrela-amadora.png',
  'famalicao': '/logos/portugal/primeira-liga/famalicao.png',
  'fc-porto': '/logos/portugal/primeira-liga/fc-porto.png',
  'porto': '/logos/portugal/primeira-liga/fc-porto.png',
  'gil-vicente': '/logos/portugal/primeira-liga/gil-vicente.png',
  'moreirense': '/logos/portugal/primeira-liga/moreirense.png',
  'nacional-de-madeira': '/logos/portugal/primeira-liga/nacional-de-madeira.png',
  'nacional': '/logos/portugal/primeira-liga/nacional-de-madeira.png',
  'rio-ave': '/logos/portugal/primeira-liga/rio-ave.png',
  'santa-clara': '/logos/portugal/primeira-liga/santa-clara.png',
  'sporting-cp': '/logos/portugal/primeira-liga/sporting-cp.png',
  'sporting': '/logos/portugal/primeira-liga/sporting-cp.png',
  'tondela': '/logos/portugal/primeira-liga/tondela.png',
  'vitoria-de-guimaraes': '/logos/portugal/primeira-liga/vitoria-de-guimaraes.png',
  'vitoria-guimaraes': '/logos/portugal/primeira-liga/vitoria-de-guimaraes.png',

  // Portugal - Liga Portugal 2
  'academico-de-viseu': '/logos/portugal/liga-portugal-2/academico-de-viseu.png',
  'benfica-b': '/logos/portugal/liga-portugal-2/benfica-b.png',
  'chaves': '/logos/portugal/liga-portugal-2/chaves.png',
  'farense': '/logos/portugal/liga-portugal-2/farense.png',
  'fc-porto-b': '/logos/portugal/liga-portugal-2/fc-porto-b.png',
  'feirense': '/logos/portugal/liga-portugal-2/feirense.png',
  'felgueiras': '/logos/portugal/liga-portugal-2/felgueiras.png',
  'leixoes': '/logos/portugal/liga-portugal-2/leixoes.png',
  'lusitania-lourosa': '/logos/portugal/liga-portugal-2/lusitania-lourosa.png',
  'maritimo': '/logos/portugal/liga-portugal-2/maritimo.png',
  'oliveirense': '/logos/portugal/liga-portugal-2/oliveirense.png',
  'pacos-de-ferreira': '/logos/portugal/liga-portugal-2/pacos-de-ferreira.png',
  'penafiel': '/logos/portugal/liga-portugal-2/penafiel.png',
  'portimonense': '/logos/portugal/liga-portugal-2/portimonense.png',
  'sporting-b': '/logos/portugal/liga-portugal-2/sporting-b.png',
  'torreense': '/logos/portugal/liga-portugal-2/torreense.png',
  'uniao-de-leiria': '/logos/portugal/liga-portugal-2/uniao-de-leiria.png',
  'vizela': '/logos/portugal/liga-portugal-2/vizela.png',
};

/**
 * Normaliza o nome do time para busca no mapa
 * - Remove acentos
 * - Converte para minúsculas
 * - Substitui espaços por hífens
 * - Remove caracteres especiais
 */
function normalizeTeamName(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove acentos
    .replace(/['']/g, '')            // Remove apóstrofes
    .replace(/&/g, 'and')            // & → and
    .replace(/\s+/g, '-')            // Espaços → hífens
    .replace(/[^a-z0-9-]/g, '')      // Remove outros caracteres
    .replace(/-+/g, '-')             // Múltiplos hífens → um hífen
    .replace(/^-|-$/g, '');          // Remove hífens nas pontas
}

/**
 * Busca o caminho da logo de um time pelo nome
 *
 * @param teamName - Nome do time (ex: "Arsenal", "Manchester City")
 * @returns Caminho da logo ou null se não encontrado
 *
 * @example
 * getTeamLogoPath("Arsenal") // "/logos/england/premier-league/arsenal.png"
 * getTeamLogoPath("Man City") // "/logos/england/premier-league/manchester-city.png"
 */
export function getTeamLogoPath(teamName: string): string | null {
  const normalized = normalizeTeamName(teamName);
  return LOGO_PATHS[normalized] || null;
}

/**
 * Busca o caminho da logo com fallback para placeholder
 *
 * @param teamName - Nome do time
 * @returns Caminho da logo ou placeholder padrão
 */
export function getTeamLogoPathWithFallback(teamName: string): string {
  return getTeamLogoPath(teamName) || '/placeholder-badge.svg';
}

/**
 * Verifica se existe logo local para um time
 */
export function hasLocalLogo(teamName: string): boolean {
  return getTeamLogoPath(teamName) !== null;
}
