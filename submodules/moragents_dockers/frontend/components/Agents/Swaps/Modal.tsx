import { Button, HStack, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Spacer, Text, useDisclosure } from '@chakra-ui/react';
import React, { FC, ComponentPropsWithoutRef, useEffect } from 'react';

export interface SwapAgentModalProps extends ComponentPropsWithoutRef<'div'> {
    isOpen: boolean;
    onClose: () => void;
}

export const SwapAgentModal: FC<SwapAgentModalProps> = ({ isOpen, onClose }) => {
    return (
        <Modal isCentered onClose={onClose} isOpen={isOpen} motionPreset='slideInBottom' closeOnOverlayClick={false}>
            <ModalOverlay />
            <ModalContent sx={{ backgroundColor: '#353936', borderColor: '#313137', color: 'white', borderRadius: '8px', padding: 1 }}>
                <ModalHeader>Swap Agent</ModalHeader>
                <ModalBody>
                    <Text sx={{ fontSize: '16px', lineHeight: '18px' }}>
                        You have switched to the Swap Agent. Please ensure you have connected your wallet and selected the correct network.
                    </Text>
                </ModalBody>
                <ModalFooter>
                    <HStack>
                        <Spacer />
                        <Button onClick={onClose} variant={'greenCustom'} sx={{ pl: 7, pr: 7 }}>Close</Button>
                    </HStack>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );
};
