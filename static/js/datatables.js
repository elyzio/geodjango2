var doc = {
    pageSize: config.pageSize,
    pageOrientation: config.orientation,
    content: [
        {
            table: {
                headerRows: 1,
                body: rows
            },
            layout: 'Borders'
        }
    ],
    styles: {
        tableHeader: {
            bold: true,
            fontSize: 10,
            color: 'white',
            fillColor: '#2d4154',
            alignment: 'center'
        },
        tableBodyEven: {},
        tableBodyOdd: {
            fillColor: '#f3f3f3'
        },
        tableFooter: {
            bold: true,
            fontSize: 10,
            color: 'white',
            fillColor: '#2d4154'
        },
        title: {
            alignment: 'center',
            fontSize: 12
        },
        message: {}
    },
    defaultStyle: {
        fontSize: 9
    }
};