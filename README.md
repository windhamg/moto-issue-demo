# moto-issue-demo

#### *adapted from [https://github.com/magicmark/moto-issue-demo](https://github.com/magicmark/moto-issue-demo)*

### Repro instructions 

```bash
$ git clone https://github.com/windhamg/moto-issue-demo.git
$ cd moto-issue-demo
$ poetry install
$ poetry run pytest -vvv
```

### Output

```
        try:
            order_breakfast()
        except BaseException as err:
>           assert 'Item' in err.response
E           AssertionError: assert 'Item' in {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'The conditional request failed'}, 'ResponseMetadata': {'HTTPHeaders': {'content-type': 'application/json', 'x-amzn-errortype': 'ConditionalCheckFailedException'}, 'HTTPStatusCode': 400, 'RetryAttempts': 0}, 'message': 'The conditional request failed'}
E            +  where {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'The conditional request failed'}, 'ResponseMetadata': {'HTTPHeaders': {'content-type': 'application/json', 'x-amzn-errortype': 'ConditionalCheckFailedException'}, 'HTTPStatusCode': 400, 'RetryAttempts': 0}, 'message': 'The conditional request failed'} = ConditionalCheckFailedException('An error occurred (ConditionalCheckFailedException) when calling the UpdateItem operation: The conditional request failed').response

tests/test_order_breakfast.py:40: AssertionError
========================================================================= short test summary info ==========================================================================
FAILED tests/test_order_breakfast.py::test_breakfast_order - AssertionError: assert 'Item' in {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'The conditional request failed'}, 'ResponseMetadata': {'HTTPHeaders'...
============================================================================ 1 failed in 0.42s =============================================================================
```

### What's the problem?

With DynamoDB+boto3, when an `update_item` operation fails due to a `ConditionExpression` failing, AND we've set `ReturnValuesOnConditionCheckFailure="ALL_OLD",` we should see the current item in the error response.

For example, if we ran `order-breakfast` when hitting DynamoDB for real, here's the output of catching the exception and pprinting `ex.response`:

```python
{
    'Error': {
        'Code': 'ConditionalCheckFailedException',
        'Message': 'The conditional request failed'
    },
    'Item': {
        'customer': {
            'S': 'mark'
        },
        'lock': {
            'M': {
                'acquired_at': {
                    'N': '123'
                }
            }
        },
        'mealtime': {
            'S': 'breakfast'
        }
    },
    'ResponseMetadata': {
        'HTTPHeaders': {
            'connection': 'keep-alive',
            'content-length': '223',
            'content-type': 'application/x-amz-json-1.0',
            'date': 'Mon, 23 Oct 2023 23:20:42 GMT',
            'server': 'Server',
            'x-amz-crc32': '3895319109',
            'x-amzn-requestid': '7RVFJQ170IU2JEIGB6VFNN73R7VV4KQNSO5AEMVJF66Q9ASUAAJG'
        },
        'HTTPStatusCode': 400,
        'RequestId': '7RVFJQ170IU2JEIGB6VFNN73R7VV4KQNSO5AEMVJF66Q9ASUAAJG',
        'RetryAttempts': 0
    }
}
```

Note that we see, `Error`, `Item`, and `ResponseMetadata`.

Under moto3, we do not see `Item`:

```python
{
    'Error': {
        'Code': 'ConditionalCheckFailedException',
        'Message': 'The conditional request failed'
    },
    'ResponseMetadata': {
        'HTTPHeaders': {
            'content-type': 'application/json',
            'x-amzn-errortype': 'ConditionalCheckFailedException'
        },
        'HTTPStatusCode': 400,
        'RetryAttempts': 0
    },
    'message': 'The conditional request failed'
}
```