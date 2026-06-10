import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/estacion.dart';
import 'auth_service.dart';

class ApiService {
  final String baseUrl = 'http://10.0.2.2:8000';

  Future<Map<String, String>> _headersConToken() async {
    final token = await AuthService().getToken();

    if (token == null || token.isEmpty) {
      throw Exception('Sesión expirada. Inicia sesión nuevamente.');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  Future<List<Estacion>> fetchEstaciones() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/estaciones/'))
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final List<dynamic> jsonResponse = json.decode(response.body);

        return jsonResponse
            .map((data) => Estacion.fromJson(data as Map<String, dynamic>))
            .toList();
      }

      throw Exception('Error del servidor: ${response.statusCode}');
    } catch (e) {
      throw Exception('No se pudo conectar con SMAT. ¿Está el servidor activo?');
    }
  }

  Future<bool> crearEstacion(String nombre, String ubicacion) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/estaciones/'),
            headers: await _headersConToken(),
            body: jsonEncode({
              'nombre': nombre,
              'ubicacion': ubicacion,
            }),
          )
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<bool> editarEstacion(
    int id,
    String nombre,
    String ubicacion,
  ) async {
    try {
      final response = await http
          .put(
            Uri.parse('$baseUrl/estaciones/$id'),
            headers: await _headersConToken(),
            body: jsonEncode({
              'nombre': nombre,
              'ubicacion': ubicacion,
            }),
          )
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<bool> eliminarEstacion(int id) async {
    try {
      final response = await http
          .delete(
            Uri.parse('$baseUrl/estaciones/$id'),
            headers: await _headersConToken(),
          )
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}