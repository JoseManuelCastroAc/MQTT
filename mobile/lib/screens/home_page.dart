import 'package:flutter/material.dart';

import '../models/estacion.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'add_estacion.dart';
import 'login_screen.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final ApiService apiService = ApiService();

  late Future<List<Estacion>> futureEstaciones;

  @override
  void initState() {
    super.initState();
    futureEstaciones = apiService.fetchEstaciones();
  }

  Future<void> _refrescarEstaciones() async {
    setState(() {
      futureEstaciones = apiService.fetchEstaciones();
    });

    await futureEstaciones;
  }

  Color _colorPorLectura(Estacion estacion) {
    final valor = estacion.ultimoValor;

    if (valor == null) return Colors.grey;
    if (valor > 50) return Colors.red;
    return Colors.green;
  }

  String _textoLectura(Estacion estacion) {
    final valor = estacion.ultimoValor;

    if (valor == null) {
      return 'Sin lectura registrada';
    }

    return 'Última lectura: ${valor.toStringAsFixed(2)}';
  }

  Future<bool> _confirmarEliminar(Estacion estacion) async {
    final respuesta = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Eliminar estación'),
          content: Text('¿Deseas eliminar "${estacion.nombre}"?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: const Text('Eliminar'),
            ),
          ],
        );
      },
    );

    return respuesta ?? false;
  }

  Future<bool> _eliminarEstacion(Estacion estacion) async {
    final confirmado = await _confirmarEliminar(estacion);

    if (!confirmado) {
      return false;
    }

    final ok = await apiService.eliminarEstacion(estacion.id);

    if (!mounted) return false;

    if (ok) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${estacion.nombre} eliminada')),
      );

      await _refrescarEstaciones();
      return true;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('No se pudo eliminar la estación'),
      ),
    );

    return false;
  }

  void _mostrarDialogoEdicion(Estacion estacion) {
    final nombreCtrl = TextEditingController(text: estacion.nombre);
    final ubicacionCtrl = TextEditingController(text: estacion.ubicacion);
    bool guardando = false;

    showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Editar Estación'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: nombreCtrl,
                    enabled: !guardando,
                    decoration: const InputDecoration(
                      labelText: 'Nombre',
                    ),
                  ),
                  TextField(
                    controller: ubicacionCtrl,
                    enabled: !guardando,
                    decoration: const InputDecoration(
                      labelText: 'Ubicación',
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: guardando
                      ? null
                      : () {
                          nombreCtrl.dispose();
                          ubicacionCtrl.dispose();
                          Navigator.pop(dialogContext);
                        },
                  child: const Text('Cancelar'),
                ),
                ElevatedButton(
                  onPressed: guardando
                      ? null
                      : () async {
                          final nombre = nombreCtrl.text.trim();
                          final ubicacion = ubicacionCtrl.text.trim();

                          if (nombre.isEmpty || ubicacion.isEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Completa todos los campos'),
                              ),
                            );
                            return;
                          }

                          setDialogState(() => guardando = true);

                          final ok = await apiService.editarEstacion(
                            estacion.id,
                            nombre,
                            ubicacion,
                          );

                          if (!mounted) return;

                          setDialogState(() => guardando = false);

                          if (ok) {
                            nombreCtrl.dispose();
                            ubicacionCtrl.dispose();

                            Navigator.pop(dialogContext);

                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Estación actualizada'),
                              ),
                            );

                            await _refrescarEstaciones();
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('No se pudo actualizar'),
                              ),
                            );
                          }
                        },
                  child: guardando
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Guardar'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _abrirCrearEstacion() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => const AddEstacionScreen(),
      ),
    );

    if (!mounted) return;

    if (result == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Estación creada con éxito')),
      );

      await _refrescarEstaciones();
    }
  }

  Future<void> _cerrarSesion() async {
    await AuthService().logout();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
      (route) => false,
    );
  }

  Widget _buildLista(List<Estacion> estaciones) {
    if (estaciones.isEmpty) {
      return RefreshIndicator(
        onRefresh: _refrescarEstaciones,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: const [
            SizedBox(height: 180),
            Center(child: Text('No hay estaciones registradas.')),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refrescarEstaciones,
      child: ListView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        itemCount: estaciones.length,
        itemBuilder: (context, index) {
          final estacion = estaciones[index];

          return Dismissible(
            key: Key(estacion.id.toString()),
            direction: DismissDirection.endToStart,
            confirmDismiss: (direction) => _eliminarEstacion(estacion),
            background: Container(
              color: Colors.red,
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: 20),
              child: const Icon(
                Icons.delete,
                color: Colors.white,
              ),
            ),
            child: ListTile(
              leading: Icon(
                Icons.sensors,
                color: _colorPorLectura(estacion),
              ),
              title: Text(estacion.nombre),
              subtitle: Text(
                '${estacion.ubicacion}\n${_textoLectura(estacion)}',
              ),
              isThreeLine: true,
              trailing: const Icon(Icons.edit),
              onTap: () => _mostrarDialogoEdicion(estacion),
            ),
          );
        },
      ),
    );
  }

  Widget _buildError(Object error) {
    return RefreshIndicator(
      onRefresh: _refrescarEstaciones,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        children: [
          const SizedBox(height: 120),
          const Icon(
            Icons.wifi_off,
            color: Colors.red,
            size: 72,
          ),
          const SizedBox(height: 16),
          const Text(
            'No se pudo cargar la información',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            error.toString().replaceFirst('Exception: ', ''),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _refrescarEstaciones,
            icon: const Icon(Icons.refresh),
            label: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        actions: [
          IconButton(
            onPressed: _cerrarSesion,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return _buildError(snapshot.error!);
          }

          return _buildLista(snapshot.data ?? []);
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _abrirCrearEstacion,
        child: const Icon(Icons.add),
      ),
    );
  }
}