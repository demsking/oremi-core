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

@TestOn('vm')
import 'dart:async';
import 'dart:io';

import 'package:mockito/mockito.dart';
import 'package:oremi_core/oremi_core.dart';
import 'package:test/test.dart';
import 'package:web_socket_channel/io.dart';

class MockIOWebSocketChannel extends Mock implements IOWebSocketChannel {}
class StreamSinkMock extends Mock implements StreamSink<dynamic> {}

class TestWebsocketClient extends WebsocketClient {
  TestWebsocketClient({required String uri, required String userAgent})
      : super(uri: uri, userAgent: userAgent);

  @override
  Future<void> onMessage(WebsocketClientEventData message) async {
    sendJson({'request': message});
  }

  @override
  void onConnectionClose(int? closeCode, String? closeReason) {
    expect(closeCode, equals(5678));
    expect(closeReason, equals('raisin'));
  }
}

void main() {
  group('WebsocketClient', () {
    HttpServer server;

    test('communicates using existing WebSockets', () async {
      server = await HttpServer.bind('localhost', 0);
      addTearDown(server.close);
      server.transform(WebSocketTransformer()).listen((WebSocket webSocket) {
        final channel = IOWebSocketChannel(webSocket);
        channel.sink.add('hello!');
        channel.stream.listen((request) {
          expect(request, equals('{"request":"hello!"}'));
          channel.sink.close(5678, 'raisin');
        });
      });

      final client = TestWebsocketClient(uri: 'ws://localhost:${server.port}', userAgent: 'test-agent');

      expect(client.connect(), completes);
    });
  });
}
