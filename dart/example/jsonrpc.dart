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
import 'dart:io';

import 'package:args/args.dart';
import 'package:oremi_core/src/wsjsonrpc.dart';

Future<void> main(List<String> args) async {
  final completer = Completer<void>();
  final parser = ArgParser()
    ..addOption(
      'host',
      abbr: 'h',
      defaultsTo: 'localhost',
      help: 'Host address to connect to (default: localhost).',
    )
    ..addOption(
      'port',
      abbr: 'p',
      defaultsTo: '7845',
      help: 'Port number to connect to (default: 7845).',
    )
    ..addOption(
      'cert-file',
      help: 'Path to the certificate file for secure connection.',
    );

  final argResults = parser.parse(args);
  final host = '${argResults['host']}:${argResults['port']}';
  SecurityContext? sslContext;

  if (argResults['cert-file'] != null) {
    print('Using certificate file "${argResults['cert-file']}"');
    sslContext = SecurityContext.defaultContext;
    sslContext.setTrustedCertificates(argResults['cert-file']);
  }

  final client = WebsocketJsonRpcClient(
    uri: sslContext != null ? 'wss://$host' : 'ws://$host',
    userAgent: 'myapp/1.0.0',
  );

  await client.connect();
  await client.sendRequest('register', params: {'status': 'online'}, onResponse: (result) async {
    print('Result: $result');
    await client.disconnect();
    completer.complete();
  });

  // Wait for the connection to complete before exiting
  await completer.future;
}
