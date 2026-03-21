import ExcelJS from 'exceljs';

export const config = {
    api: {
        bodyParser: {
            sizeLimit: '10mb',
        },
    },
};

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Método no permitido' });
    }

    try {
        const { ordenes, config: cfg } = req.body;

        if (!ordenes || !ordenes.length) {
            return res.status(400).json({ error: 'No hay órdenes' });
        }

        const workbook = new ExcelJS.Workbook();
        const ws = workbook.addWorksheet('A domicilio');
        
        const headers = [
            'Paquete Guardado', 'Peso (grs)', 'Alto (cm)', 'Ancho (cm)', 'Profundidad (cm)',
            'Valor declarado ($ C/IVA) *', 'Numero Interno', 'Nombre *', 'Apellido *', 'DNI *',
            'Email *', 'Celular código *', 'Celular número *', 'Calle *', 'Número *',
            'Piso', 'Departamento', 'Provincia / Localidad / CP *', 'Observaciones'
        ];

        ws.addRow([]);
        ws.addRow(headers);

        ordenes.forEach(o => {
            ws.addRow([
                '', o.peso, o.alto, o.ancho, o.prof, o.valor, o.numeroInterno,
                o.nombre, o.apellido, o.dni, o.email, o.celCodigo, o.celNumero,
                o.calle, o.numero, o.piso, o.depto, o.ubicacion, o.observaciones
            ]);
        });

        ws.columns = [
            { width: 15 }, { width: 10 }, { width: 10 }, { width: 10 }, { width: 12 },
            { width: 18 }, { width: 12 }, { width: 15 }, { width: 15 }, { width: 12 },
            { width: 25 }, { width: 12 }, { width: 12 }, { width: 25 }, { width: 10 },
            { width: 8 }, { width: 12 }, { width: 40 }, { width: 30 }
        ];

        const buffer = await workbook.xlsx.writeBuffer();

        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        res.setHeader('Content-Disposition', `attachment; filename=Andreani_${ordenes.length}_ordenes.xlsx`);
        res.send(Buffer.from(buffer));

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Error generando Excel', details: error.message });
    }
}
