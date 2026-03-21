export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    const { storeId, accessToken } = req.query;

    if (!storeId || !accessToken) {
        return res.status(400).json({ error: 'Faltan storeId o accessToken' });
    }

    try {
        const response = await fetch(
            `https://api.tiendanube.com/v1/${storeId}/orders?per_page=50`,
            {
                headers: {
                    'Authentication': `bearer ${accessToken}`,
                    'User-Agent': 'Andreani Generator (santimktonline@gmail.com)',
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            const errorText = await response.text();
            return res.status(response.status).json({ error: 'Error de Tienda Nube', details: errorText });
        }

        const data = await response.json();
        return res.status(200).json(data);

    } catch (error) {
        return res.status(500).json({ error: 'Error de conexión', details: error.message });
    }
}
