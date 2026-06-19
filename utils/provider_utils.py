def select_provider(providers: dict):
    providers_names = list(providers.keys())

    if len(providers_names) < 2:
        print("\nOnly one provider available. Using the default provider.")
        return (providers[providers_names[0]],)

    while True:
        print(f"\nAvailable providers: {', '.join(providers_names)}.")
        selection = input("- Select main provider (or press Enter for default): ").strip()

        # User pressed Enter without typing
        if not selection:
            return (providers[providers_names[0]], providers[providers_names[1]])

        # User made a selection, validate it
        matched_provider = next(
            (name for name in providers_names if name.lower() == selection.lower()), None
        )

        if matched_provider:
            main_provider = providers[matched_provider]
            fallback_provider = next(
                name for name in providers_names if name.lower() != selection.lower()
            )
            return (main_provider, providers[fallback_provider])

        print(f"- Invalid selection '{selection}'. Please try again.")
