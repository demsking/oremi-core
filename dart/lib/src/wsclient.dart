// Copyright 2023 Sébastien Demanou. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =============================================================================

import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/io.dart';

typedef WebSocketClientEventType = String;
typedef WebSocketClientEventData = dynamic;

abstract class WebSocketClient {
  final String uri;
  final String userAgent;

  late IOWebSocketChannel _channel;
  bool _connected = false;
  bool get connected => _connected;

  WebSocketClient({
    required this.uri,
    required this.userAgent,
  });

  Future<void> onMessage(WebSocketClientEventData message);

  Future<void> onConnect() async {
    print('Connected to $uri');
  }

  void onConnectionClose(int? closeCode, String? closeReason) {
    print('Connection to $uri closed with code $closeCode, reason "$closeReason"');
  }

  Future<void> connect() async {
    print('Connecting to $uri');
    _channel = IOWebSocketChannel.connect(uri, headers: {'User-Agent': userAgent});

    await _channel.ready;
    _connected = true;

    await onConnect();
    _channel.stream.listen(
      (message) async => await onMessage(message),
      onDone: () => onConnectionClose(_channel.closeCode, _channel.closeReason),
      cancelOnError: true,
    );
  }

  Future<void> sendData(dynamic data) async {
    _channel.sink.add(data);
  }

  Future<void> sendJson(dynamic data) async {
    data = json.encode(data);

    _channel.sink.add(data);
  }

  Future<void> disconnect() async {
    if (_connected) {
      await _channel.sink.close(1000, 'Client disconnect');
      _connected = false;
    }
  }
}
