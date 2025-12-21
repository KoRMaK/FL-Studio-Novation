class SurfaceActionGeneratorExample:
    def __init__(self, action_dispatcher, product_defs):
        """
        Args:
            action_dispatcher: Used to dispatch SurfaceActions to views and the application
            product_defs: Product definitions to compare surface events against
        """

    def handle_midi_event(self, fl_event):
        """Generate and dispatch actions given an fl event.

        Note:   The dispatching can be handled by the SurfaceActionGeneratorWrapper if this
                function returns a list of actions and this instance is owned by it.

        Args:
            fl_event: Event to generate actions for (or none at all)
        """
