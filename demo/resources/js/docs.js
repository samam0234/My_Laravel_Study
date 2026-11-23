import SwaggerUI from 'swagger-ui-dist/swagger-ui-bundle.js';
import 'swagger-ui-dist/swagger-ui.css';
SwaggerUI({ url: '/openapi.json', dom_id: '#api-docs', persistAuthorization: false });
