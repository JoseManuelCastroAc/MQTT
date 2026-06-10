class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;
  final double? ultimoValor;

  const Estacion({
    required this.id,
    required this.nombre,
    required this.ubicacion,
    this.ultimoValor,
  });

  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'] as int,
      nombre: json['nombre']?.toString() ?? '',
      ubicacion: json['ubicacion']?.toString() ?? '',
      ultimoValor: json['ultimo_valor'] == null
          ? null
          : double.tryParse(json['ultimo_valor'].toString()),
    );
  }
}