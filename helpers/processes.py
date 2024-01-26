def refill_tokens(env, mtu, tokens_per_second, token_buckets):
    while True:
        yield env.timeout(mtu / tokens_per_second)
        for token_bucket in token_buckets:
            token_bucket.new_tokens()
