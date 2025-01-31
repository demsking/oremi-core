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
import 'package:oremi_core/src/wsclient.dart';

typedef ResponseCallback = dynamic Function(Map<String, dynamic>);

class InvalidMessageFormatError extends TypeError {
  final String message;
  InvalidMessageFormatError(this.message);
}

class WebSocketJsonRpcClient extends WebsocketClient {
  final Map<int, ResponseCallback> _requestCallbacks = {};
  final Map<int, ResponseCallback> _errorCallbacks = {};
  int _requestId = 1;

  WebSocketJsonRpcClient({
    required String uri,
    required String userAgent,
  }): super( uri: uri, userAgent: userAgent );

  @override
  Future<void> onMessage(WebsocketClientEventData message) async {
    final data = json.decode(message);
    if (data.containsKey('id')) {
      final requestId = data['id'];
      if (data.containsKey('error')) {
        print('< $message');
        if (_errorCallbacks.containsKey(requestId)) {
          await _errorCallbacks[requestId]!(data['error']);
          _errorCallbacks.remove(requestId);
        }
      } else {
        print('< $message');
        if (_requestCallbacks.containsKey(requestId)) {
          await _requestCallbacks[requestId]!(data['result']);
          _requestCallbacks.remove(requestId);
        }
      }
    } else {
      throw InvalidMessageFormatError('Invalid Message: $message');
    }
  }

  Future<void> sendRequest(
    String method, {
    dynamic params,
    ResponseCallback? onResponse,
    ResponseCallback? onError,
  }) async {
    final data = <String, dynamic>{
      'id': _requestId,
      'jsonrpc': '2.0',
      'method': method,
    };
    if (params != null) {
      data['params'] = params;
    }
    if (onResponse != null) {
      _requestCallbacks[_requestId] = onResponse;
    }
    if (onError != null) {
      _errorCallbacks[_requestId] = onError;
    }
    await sendJson(data);
    _requestId++;
  }
}
